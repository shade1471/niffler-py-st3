import json
import logging
from json import JSONDecodeError

import allure
import curlify
from allure_commons.types import AttachmentType
from requests import Response
from requests.structures import CaseInsensitiveDict


def allure_attach_request(function):
    """Декоратор логирования запроса, хедеров запроса, хедеров ответа в allure шаг и аллюр аттачмент и в консоль."""

    def wrapper(*args, **kwargs):
        method, url = args[1], args[2]

        from jinja2 import Environment, PackageLoader, select_autoescape
        env = Environment(
            loader=PackageLoader("resources"),
            autoescape=select_autoescape()
        )
        template = env.get_template("http-colored-request.ftl")

        with allure.step(f"{method} {url}"):

            response: Response = function(*args, **kwargs)
            curl = curlify.to_curl(response.request)

            prepare_render = {
                "request": response.request,
                "curl": curl,
            }
            render = template.render(prepare_render)

            logging.debug(curl)
            logging.debug(response.text)

            allure.attach(
                body=render,
                name=f"Request",
                attachment_type=AttachmentType.HTML,
                extension=".html"
            )

            try:
                allure.attach(
                    body=json.dumps(response.json(), indent=4).encode("utf8"),
                    name=f"Response json {response.status_code}",
                    attachment_type=AttachmentType.JSON,
                    extension=".json"
                )
            except JSONDecodeError:
                allure.attach(
                    body=response.text.encode("utf8"),
                    name=f"Response text {response.status_code}",
                    attachment_type=AttachmentType.TEXT,
                    extension=".txt")
            headers_dict = dict(response.headers)
            allure.attach(
                body=json.dumps(headers_dict, indent=4).encode("utf8"),
                name=f"Response headers {response.status_code}",
                attachment_type=AttachmentType.JSON,
                extension=".json"
            )
            return response

    return wrapper


def attach_sql(statement, parameters, context):
    statement_with_params = statement % parameters
    name = statement.split(" ")[0] + " " + context.engine.url.database
    allure.attach(statement_with_params, name=name, attachment_type=AttachmentType.TEXT)


def allure_request_logger(function):
    def wrapper(*args, **kwargs):
        response: Response = function(*args, **kwargs)
        method = response.request.method
        url = response.request.url
        logging.info(f'\n\nREQUEST {method} {url}\n\n'
                     f'REQUEST HEADERS {prettyfy_headers(response.request.headers)}\n\n'
                     f'REQUEST BODY {prettyfy_body(response.request.body)}\n\n'
                     f'RESPONSE HEADERS {prettyfy_headers(response.headers)}\n\n'
                     f'RESPONSE BODY {prettyfy_body(response.content)}\n\n')
        return response

    return wrapper


def prettyfy_headers(headers: CaseInsensitiveDict) -> str:
    if headers:
        return json_dumping(dict(headers))
    else:
        return 'None'


def prettyfy_body(body: bytes) -> str:
    if body:
        try:
            return json_dumping(json.loads(body))
        except:
            return str(body)
    else:
        return 'None'


def json_dumping(dict_to_convert: dict) -> str:
    return json.dumps(dict_to_convert, indent=2, ensure_ascii=False)
