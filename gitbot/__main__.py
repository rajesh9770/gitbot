import os
import json
import aiohttp
import argparse

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

routes = web.RouteTableDef()
router = routing.Router()
test = 1

prefix = '@bot'
parser = argparse.ArgumentParser()
parser.add_argument("-h", "--hostname", help="enter the hostname or ip address", type=str)
parser.add_argument("-p", "--port", help="enter the ssh port for the host", type=int, default=22)
parser.add_argument("-u", "--username", help="enter the ssh user name to login to the host", type=str, default='maglev')
parser.add_argument("-P", "--password", help="enter the ssh user password to login to the host", type=str, default='Maglev123')
#args = parser.parse_args(["--square", "2", "-c", "3"])
#args = parser.parse_args(cmdLine.split())

@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Whenever an issue is opened, greet the author and say thanks."""
    print(f"{test}Event: {json.dumps(event.data)}")
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]

    message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."
    await gh.post(url, data={"body": message})
    pass


#   https://developer.github.com/v3/activity/events/types/#issuecommentevent
#@router.register("issue_comment", action="edited")
@router.register("issue_comment", action="created")
async def issue_comment_created_event(event, gh, *args, **kwargs):
    """ Whenever an issue gets comment, say thanks."""
    print(f"{test}issue_comment Event: {json.dumps(event.data)}")
    #url = event.data["issue"]["comments_url"]
    author = event.data["comment"]["user"]["login"]
    comment = event.data["comment"]["body"]
    for line in comment.splitlines():
        if line.startswith(prefix):
            args = parser.parse_args(line[len(prefix):])
            print (f"args.password {args.password} args.username {args.username} args.port {args.port} args.hostname {args.hostname}")

    message = f"Thanks for the report @{author}! Replaying comment {comment} (I'm a bot)."
    print(f'Comment received {message}')
    pass

# https://developer.github.com/v3/activity/events/types/#pullrequestevent
@router.register("pull_request", action="opened")
async def pull_request_opened_event(event, gh, *args, **kwargs):
    """ Whenever a pull request is open, say thanks."""
    print(f"{test}pull_request_opened Event: {json.dumps(event.data)}")
    author = event.data["pull_request"]["user"]["login"]
    comment = event.data["pull_request"]["body"]

    message = f"Thanks for the pull request @{author}! Replaying comment {comment} (I'm a bot)."
    print(f'Comment received {message}')
    pass


@router.register("pull_request", action="edited")
async def pull_request_edited_event(event, gh, *args, **kwargs):
    """ Whenever a pull request is edited, say thanks."""
    print(f"{test}pull_request_edited Event: {json.dumps(event.data)}")
    author = event.data["pull_request"]["user"]["login"]
    changes = event.data["changes"]["body"]

    message = f"{test}Thanks for the comment on pull request @{author}! Replaying comment {changes} (I'm a bot)."
    print(f'Comment received {message}')
    pass


@routes.post("/")
async def main(request):
    # read the GitHub webhook payload
    body = await request.read()

    # our authentication token and secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # a representation of GitHub webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # instead of mariatta, use your own username
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "rajesh9770", oauth_token=oauth_token)

        # call the appropriate callback for the event
        await router.dispatch(event, gh)

    # return a "Success"
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
