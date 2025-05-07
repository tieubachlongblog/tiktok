from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright

app = FastAPI()

class TikTokRequest(BaseModel):
    url: str

@app.post("/download")
async def download_video(request: TikTokRequest):
    url = request.url
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("video", timeout=10000)
            video_tag = await page.query_selector("video")
            video_url = await video_tag.get_attribute("src")
            await browser.close()
            if video_url and video_url.startswith("https://"):
                return {"status": "success", "video_url": video_url}
            raise HTTPException(status_code=404, detail="Không tìm thấy video.")
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Lỗi: {e}")
