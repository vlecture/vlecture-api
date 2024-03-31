#!/bin/bash
echo "What are you updating in this migration? [Input and enter]"

read msg

alembic revision --autogenerate -m $msg
alembic upgrade head