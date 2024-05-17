import logging
from dataclasses import dataclass
from django.template.loader import render_to_string
from channels.generic.http import AsyncHttpConsumer
from channels.db import database_sync_to_async
from sse.events.models import Task

log = logging.getLogger(__name__)


@dataclass
class SerializedTask:
    title: str
    description: str
    assigned_to: str
    created_by: str
    due_by: str

    @classmethod
    def to_obj(cls, task: Task):
        return cls(
            **{
                "title": task.title,
                "description": task.description,
                "assigned_to": task.assigned_to.username,
                "created_by": task.created_by.username,
                "due_by": task.due_by.strftime("%d/%M/%y %h:%m:%s"),
            }
        )

    @classmethod
    def to_dict(cls, task: Task) -> dict:
        return {
            "title": task.title,
            "description": task.description,
            "assigned_to": task.assigned_to.username,
            "created_by": task.created_by.username,
            "due_by": task.due_by.strftime("%d/%M/%y %h:%m:%s"),
        }


class ServerSentEventsConsumer(AsyncHttpConsumer):

    async def handle(self, body):
        log.info(f"Adding group {self.scope['user']}")
        await self.channel_layer.group_add(
            f"sse_{self.scope['user']}", self.channel_name
        )
        await self.send_headers(
            headers=[
                (b"Cache-Control", b"no-cache"),
                (
                    b"Content-Type",
                    b"text/event-stream",
                ),  # This header indicates that the response is of type SSE
                (
                    b"Transfer-Encoding",
                    b"chunked",
                ),  # Indicates that data is to be sent in a series of chunks, and total size is unknown
                (b"Connection", b"keep-alive"),
            ]
        )
        # Headers are only sent after the first body event.
        # Set "more_body" to tell the interface server to not
        # finish the response yet:
        payload = "\n".join(["event: ping", "data: pong"]) + "\n\n\n"
        await self.send_body(payload.encode("utf-8"), more_body=True)

    def get_user_tasks(self):
        return [
            SerializedTask.to_obj(task)
            for task in Task.objects.filter(assigned_to=self.scope["user"])
        ]

    async def sse_event(self, event: dict):
        log.info("send event triggered")
        task = SerializedTask(**event["task"])
        # Send task detail event
        tasks = await database_sync_to_async(self.get_user_tasks)()
        task_detail = ""
        for task_obj in tasks:
            task_detail += render_to_string("task.html", {"task": task_obj}).replace(
                "\n", ""
            )
        data = f"event: task_event\ndata: {task_detail}\n\n"
        await self.send_body(data.encode("utf-8"), more_body=True)

        # Send task notification event
        task_notification = render_to_string(
            "notification.html", {"task": task}
        ).replace("\n", "")
        data = f"event: notification_event\ndata: {task_notification}\n\n"
        await self.send_body(data.encode("utf-8"), more_body=True)

    async def disconnect(self):
        await self.channel_layer.group_discard(
            f"sse_{self.scope['user']}", self.channel_name
        )

    async def http_request(self, message):
        """
        Receives an SSE request and holds the connection open until the client chooses to disconnect.
        """
        try:
            await self.handle(b"".join(self.body))
        finally:
            pass
