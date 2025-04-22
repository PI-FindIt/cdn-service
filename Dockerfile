FROM ghcr.io/astral-sh/uv:python3.13-alpine
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV ENV development

ENV PATH="/cdn-service/.venv/bin:$PATH"

WORKDIR /cdn-service

RUN pip uninstall multipart && pip install --no-cache uv python-multipart

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen

EXPOSE 8000
CMD [ "/cdn-service/entrypoint.sh" ]
