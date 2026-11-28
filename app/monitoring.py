
import httpx
import time


def check_website(url):
    start_time = time.perf_counter()

    try:
        response = httpx.get(
            url,
            timeout=10,
            follow_redirects=True
        )

        end_time = time.perf_counter()
        response_time = (end_time - start_time) * 1000

        return {
            "status_code": response.status_code,
            "response_time": round(response_time, 2),
            "is_success": response.is_success
        }

    except httpx.RequestError as e:
        end_time = time.perf_counter()
        response_time = (end_time - start_time) * 1000

        print(f"Request failed for {url}: {e}")

        return {
            "status_code": None,
            "response_time": round(response_time, 2),
            "is_success": False
        }
