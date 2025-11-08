import logging
import time
from datetime import datetime, timedelta
from http import HTTPStatus

import uvicorn
from volt import Request, Response, Volt, config, http

from components_gen import (
    BaseNavbar,
    Demo,
    DemoChatMessages,
    DemoCounter,
    DemoProgrammingLanguageList,
    DemoTaskList,
    Features,
    Home,
)
from custom_types import (
    DemoChatMessagesTypes,
    DemoProgrammingLanguage,
    Message,
    NavSelected,
    Sender,
)

mw_log = logging.getLogger("volt.middleware.py")
log = logging.getLogger("volt.py")

app = Volt(static_location="static")


@app.middleware
async def logging_middleware(request: Request, handler: http.Handler) -> Response:
    start = time.time()
    response = await handler(request)
    end = time.time() - start
    mw_log.info(f"Request - Path: {request.path}, Time: {end * 1_000 * 1_000}μs")
    return response


@app.middleware
async def auth(request: Request, handler: http.Handler) -> Response:
    auth_success = True
    if auth_success:
        return await handler(request)
    return Response(body="get outta here!", status=HTTPStatus.FORBIDDEN)


@app.middleware
async def origin(request: Request, handler: http.Handler) -> Response:
    allowed_hosts = config.allowed_hosts
    host = None
    for header in request.headers:
        if header.name.lower() == "host":
            host = header.value
            if host in allowed_hosts:
                return await handler(request)

    if not host:
        return Response(status=HTTPStatus.BAD_REQUEST)

    log.warning("request from host %s blocked", host)
    return Response(status=HTTPStatus.FORBIDDEN)


@app.route("/", method="GET")
async def root(request: Request) -> Response:
    context = Home.Context(
        request=request,
        selected=NavSelected.HOME,
        oob=[BaseNavbar(BaseNavbar.Context(request=request, selected=NavSelected.HOME, oob=[]))],
    )
    return Response(
        Home(context).render(request),
    )


@app.route("/features", method="GET")
async def features(request: Request) -> Response:
    context = Features.Context(
        request=request,
        selected=NavSelected.FEATURES,
        oob=[BaseNavbar(BaseNavbar.Context(request=request, selected=NavSelected.FEATURES, oob=[]))],
    )
    return Response(Features(context).render(request))


# fmt: off
PROGRAMMING_LANGUAGES: list[DemoProgrammingLanguage] = [
    DemoProgrammingLanguage("Python", "Py", "High-level programming language", "Popular", "text-volt-yellow", "bg-volt-yellow/20"),
    DemoProgrammingLanguage("JavaScript", "JS", "Dynamic web programming language", "Web", "text-blue-400", "bg-blue-400/20"),
    DemoProgrammingLanguage("TypeScript", "TS", "Typed superset of JavaScript", "Web", "text-blue-500", "bg-blue-500/20"),
    DemoProgrammingLanguage("Rust", "Rs", "Systems programming language", "Systems", "text-orange-400", "bg-orange-400/20"),
    DemoProgrammingLanguage("Go", "Go", "Google's systems language", "Systems", "text-cyan-400", "bg-cyan-400/20"),
    DemoProgrammingLanguage("Java", "Jv", "Enterprise programming language", "Enterprise", "text-red-400", "bg-red-400/20"),
    DemoProgrammingLanguage("C++", "C+", "Low-level systems language", "Systems", "text-purple-400", "bg-purple-400/20"),
    DemoProgrammingLanguage("C#", "C#", "Microsoft's .NET language", "Enterprise", "text-green-400", "bg-green-400/20"),
    DemoProgrammingLanguage("Zig", "Zg", "Modern systems programming", "Systems", "text-volt-yellow", "bg-volt-yellow/20"),
    DemoProgrammingLanguage("Swift", "Sw", "Apple's iOS development language", "Mobile", "text-orange-500", "bg-orange-500/20"),
    DemoProgrammingLanguage("Kotlin", "Kt", "Modern Android development", "Mobile", "text-purple-500", "bg-purple-500/20"),
    DemoProgrammingLanguage("Ruby", "Rb", "Developer-friendly scripting", "Web", "text-red-500", "bg-red-500/20"),
    DemoProgrammingLanguage("PHP", "Php", "Server-side web language", "Web", "text-indigo-400", "bg-indigo-400/20"),
    DemoProgrammingLanguage("Dart", "Dt", "Google's Flutter language", "Mobile", "text-blue-600", "bg-blue-600/20"),
    DemoProgrammingLanguage("Elixir", "Ex", "Functional concurrent language", "Functional", "text-purple-600", "bg-purple-600/20"),
    DemoProgrammingLanguage("Haskell", "Hs", "Pure functional language", "Functional", "text-green-500", "bg-green-500/20"),
    DemoProgrammingLanguage("Clojure", "Cl", "Modern Lisp for JVM", "Functional", "text-cyan-500", "bg-cyan-500/20"),
    DemoProgrammingLanguage("Scala", "Sc", "Functional + OOP on JVM", "Enterprise", "text-red-600", "bg-red-600/20"),
    DemoProgrammingLanguage("R", "R", "Statistical computing language", "Data", "text-blue-700", "bg-blue-700/20"),
    DemoProgrammingLanguage("Julia", "Jl", "High-performance scientific computing", "Data", "text-purple-700", "bg-purple-700/20"),
]
# fmt: on


@app.route("/demo/counter/{direction:str}", method="POST")
async def demo_counter(request: Request) -> Response:
    value = request.form_data.get("value", [])

    if len(value) == 0:
        log.warning("given value is empty")
        return Response(status=HTTPStatus.BAD_REQUEST)

    try:
        int_value = int(value[0])
    except Exception as e:
        log.warning(f"error converting value to integer: {e}")
        return Response(status=HTTPStatus.BAD_REQUEST)

    match request.route_params.get("direction"):
        case "increment":
            int_value += 1
        case "decrement":
            int_value -= 1
        case "reset":
            int_value = 0
        case _:
            return Response(status=HTTPStatus.NOT_FOUND)

    context = DemoCounter.Context(
        request=request,
        value=int_value,
        oob=[],
    )

    return Response(DemoCounter(context).render(request))


@app.route("/demo/languages/search", method="GET")
async def demo_languages_search(request: Request) -> Response:
    query = request.query_params.get("query")
    if query is None or len(query) == 0:
        context = DemoProgrammingLanguageList.Context(
            request=request,
            programming_languages=[],
            searching=False,
            oob=[],
        )
        return Response(DemoProgrammingLanguageList(context).render(request))

    results: list[DemoProgrammingLanguage] = []
    for language in PROGRAMMING_LANGUAGES:
        if query[0].lower() in language.name.lower():
            results.append(language)

        # Just take top 5 results
        if len(results) >= 3:
            break

    context = DemoProgrammingLanguageList.Context(
        request=request,
        programming_languages=results,
        searching=True,
        oob=[],
    )

    return Response(DemoProgrammingLanguageList(context).render(request))


@app.route("/demo/add-task", method="POST")
async def demo_add_task(request: Request) -> Response:
    task = request.form_data.get("task")
    if task is None:
        return Response(status=HTTPStatus.BAD_REQUEST)

    context = DemoTaskList.Context(
        request=request,
        tasks=task,  # takes a list
        oob=[],
    )
    return Response(DemoTaskList(context).render(request))


@app.route("/demo/task/delete", method="DELETE")
async def demo_delete_task(_request: Request) -> Response:
    return Response(status=HTTPStatus.OK)


CHAT_MESSAGES: DemoChatMessagesTypes.chat_messages = [
    {
        "message": "This is amazing!",
        "sender": Sender.ME,
        "time": datetime.now() - timedelta(minutes=2),
    },
    {
        "message": "Glad you like it! Volt makes real-time features super easy.",
        "sender": Sender.THEM,
        "time": datetime.now() - timedelta(minutes=1),
    },
    {
        "message": "The performance is incredible 🚀",
        "sender": Sender.ME,
        "time": datetime.now(),
    },
]


@app.route("/demo/chat", method="POST")
async def demo_add_chat(request: Request) -> Response:
    chat = request.form_data.get("message", [])
    if len(chat) != 1:
        log.warning(f"unexpected chat length: {len(chat)}")
        return Response(status=HTTPStatus.BAD_REQUEST)

    messages: list[Message] = [
        {
            "message": chat[0],
            "sender": Sender.ME,
            "time": datetime.now(),
        }
    ]

    context = DemoChatMessages.Context(
        request=request,
        chat_messages=messages,
        oob=[],
    )
    return Response(DemoChatMessages(context).render(request))


@app.route("/demo", method="GET")
async def demo(request: Request) -> Response:
    tasks = [
        "Learn about Volt framework",
        "Try HTMX integration",
        "Add a new task!",
    ]

    context = Demo.Context(
        request=request,
        selected=NavSelected.DEMO,
        tasks=tasks,
        searching=False,
        programming_languages=[],
        value=0,
        chat_messages=CHAT_MESSAGES,
        oob=[BaseNavbar(BaseNavbar.Context(request=request, selected=NavSelected.DEMO, oob=[]))],
    )

    return Response(Demo(context).render(request))


@app.route("/quickstart", method="GET")
async def quickstart(_: Request) -> Response:
    return http.Redirect("/")


@app.route("/home", method="GET")
async def home(_: Request) -> Response:
    return http.Redirect("/")


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=config.server_host,
        port=config.server_port,
        log_level=config.log_level.lower(),
        reload=config.debug,
    )
