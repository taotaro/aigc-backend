"""
存放各种工具
"""
import asyncio
import json
import os
import pathlib
import ssl
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPException
from socket import socket, AF_INET, SOCK_DGRAM

from jinja2 import Environment, FileSystemLoader

from app.config import get_settings

__all__ = (
    'render_template',
)



def render_template(template_name: str, render_data: dict) -> str:
    # Create an Environment object that specifies how the template will be loaded as a file system
    env = Environment(loader=FileSystemLoader(f'{pathlib.Path(__file__).resolve().parent.parent}/templates'))
    # Load a template file, the contents of which is an HTML page with some placeholders
    template = env.get_template(template_name)
    # Call the template's render method, pass in the data, and get the final document.
    return template.render({'data': render_data})