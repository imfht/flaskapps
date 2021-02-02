import asyncio
from aiohttp import ClientSession
import pathlib
async def main():
    url = 'https://www.boxofficemojo.com/year/2019/'
    html_body = ""
    async with ClientSession() as session:
        async with session.get(url) as response:
            html_body = await response.read()
            return html_body


html_data = asyncio.run(main())
output_dir = pathlib.Path().resolve() / "snapshots"
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "2019.html"
output_file.write_text(html_data.decode())
# with open('path/to/output', 'w') as f:
#     f.write(html_data.decode())