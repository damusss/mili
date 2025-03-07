import pygame
import os
import io
import threading
import typing
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

__all__ = ("get", "get_google", "preload", "preload_google", "setup")

_temp_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
_gmi_svgs = {}
_gmi_surfs = {}
_fileicons = {}
_fileicons_col = {}
_settings = {
    "path": "",
    "color": "black",
    "svg_size": 24,
    "google_cache": True,
    "source_col": "white",
    "file_type": "png",
}


def _get_svg_async(name, cache):
    path = os.path.join(_settings["path"], f"gmi_{name}.svg")
    size = (_settings["svg_size"], _settings["svg_size"])
    if os.path.exists(path):
        try:
            image = pygame.image.load_sized_svg(path, size)
            _gmi_svgs[name] = image
            return
        except pygame.error:
            ...
    try:
        with urllib.request.urlopen(
            f"https://fonts.gstatic.com/s/i/materialicons/{name}/v6/24px.svg"
        ) as response:
            if response.status != 200:
                if response.status == 404:
                    _gmi_svgs[name] = 404
                else:
                    del _gmi_svgs[name]
                return
            content = response.read()
            buffer = io.BytesIO(content)
            image = pygame.image.load_sized_svg(buffer, size)
            _gmi_svgs[name] = image
            if _settings["google_cache"] and cache:
                with open(path, "wb") as file:
                    file.write(content)
            return

    except urllib.error.HTTPError as e:
        if e.code == 404:
            _gmi_svgs[name] = 404
        else:
            del _gmi_svgs[name]
        return
    except urllib.error.URLError:
        del _gmi_svgs[name]
        return


def _get_file_async(name):
    path = os.path.join(_settings["path"], f"{name}.{_settings["file_type"]}")
    try:
        image = pygame.image.load(path)
        _fileicons[name] = image
    except Exception:
        _fileicons[name] = "error"


def _get_svg_file_async(name):
    path = os.path.join(_settings["path"], f"{name}.png")
    try:
        image = pygame.image.load_sized_svg(path, _settings["svg_size"])
        _fileicons[name] = image
    except Exception:
        _fileicons[name] = "error"


def _colorize_google(icon_name, color, key):
    icon = _gmi_svgs[icon_name]
    if icon == "loading":
        return _temp_surf
    elif icon == 404:
        raise NameError(f"Google icon {icon_name} is not a valid google icon")
    ret: pygame.Surface = icon.copy()
    if color is not None:
        ret.fill(color, special_flags=pygame.BLEND_RGB_ADD)
    _gmi_surfs[key] = ret
    return ret


def _colorize_file(icon_name, color, key):
    icon = _fileicons[icon_name]
    if icon == "loading":
        return _temp_surf
    elif icon == "error":
        raise IOError(f"File icon {icon_name} wasn't found/could not be loaded")
    ret: pygame.Surface = icon.copy()
    if color is not None:
        ret.fill(
            color,
            special_flags=(
                pygame.BLEND_RGB_ADD
                if _settings["source_col"] == "black"
                else pygame.BLEND_RGBA_MULT
            ),
        )
    _fileicons_col[key] = ret
    return ret


def setup(
    path: str,
    color: pygame.typing.ColorLike|None,
    source_color: typing.Literal["white", "black"] = "white",
    svg_size: int = 24,
    google_cache: bool = True,
    file_type: str = "png",
):
    _settings.update(
        {
            "path": path,
            "color": color,
            "svg_size": svg_size,
            "google_cache": google_cache,
            "source_col": source_color,
            "file_type": file_type
        }
    )


def get_google(icon_name: str, color: pygame.typing.ColorLike|None=None, do_async: bool = True, cache: bool = True):
    if color is None:
        color = _settings["color"]
    key = f"{icon_name}_{color}"
    if key in _gmi_surfs:
        return _gmi_surfs[key]
    if icon_name in _gmi_svgs:
        return _colorize_google(icon_name, color, key)
    if do_async:
        _gmi_svgs[icon_name] = "loading"
        thread = threading.Thread(target=_get_svg_async, args=(icon_name, cache))
        thread.start()
        return _temp_surf
    else:
        _get_svg_async(icon_name, cache)
        if icon_name not in _gmi_svgs:
            return _temp_surf
        return _colorize_google(icon_name, color, key)


def get(icon_name: str, color: pygame.typing.ColorLike|None=None, do_async: bool = True, svg: bool = False):
    if color is None:
        color = _settings["color"]
    key = f"{icon_name}_{color}"
    if key in _fileicons_col:
        return _fileicons_col[key]
    if icon_name in _fileicons:
        return _colorize_file(icon_name, color, key)
    if do_async:
        _fileicons[icon_name] = "loading"
        thread = threading.Thread(
            target=(_get_svg_file_async if svg else _get_file_async), args=(icon_name,)
        )
        thread.start()
        return _temp_surf
    else:
        if svg:
            _get_svg_file_async(icon_name)
        else:
            _get_file_async(icon_name)
        return _colorize_file(icon_name, color, key)


def get_svg(icon_name: str, color: pygame.typing.ColorLike|None=None, do_async: bool = True):
    return get(icon_name, color, do_async, True)


def preload_google(*icon_names: str, do_async: bool = True, cache: bool = True):
    if do_async:
        for icon in icon_names:
            _gmi_svgs[icon] = "loading"
        with ThreadPoolExecutor(max_workers=len(icon_names)) as pool:
            for icon in icon_names:
                pool.submit(_get_svg_async, icon, cache)
    else:
        for icon in icon_names:
            _get_svg_async(icon, cache)
            if icon in _gmi_svgs:
                if _gmi_svgs[icon] == 404:
                    raise NameError(f"Google icon {icon} is not a valid google icon")


def preload(*icon_names: str, do_async: bool = True, svg: bool = False):
    if do_async:
        for icon in icon_names:
            _fileicons[icon] = "loading"
        with ThreadPoolExecutor(max_workers=len(icon_names)) as pool:
            for icon in icon_names:
                pool.submit((_get_svg_file_async if svg else _get_file_async), icon)
    else:
        for icon in icon_names:
            if svg:
                _get_svg_file_async(icon)
            else:
                _get_file_async(icon)
            if _fileicons[icon] == "error":
                raise IOError(f"File icon {icon} wasn't found/could not be loaded")
