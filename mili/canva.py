import pygame
import typing
from pygame._sdl2 import video as pgvideo


class _AbstractCanva:
    backend: str
    _rect: pygame.Rect
    _offset: pygame.Vector2
    _renderer: pgvideo.Renderer
    _surface: pygame.Surface
    surface: pygame.Surface
    renderer: pgvideo.Renderer

    @property
    def rect(self):
        return self._rect

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = pygame.Vector2(value)

    def _active(self):
        return self._surface is not None or self._renderer is not None

    def _get_clip(self) -> pygame.Rect: ...
    def _set_clip(self, rect: pygame.Rect): ...
    def _draw_line(self, color, start, end, width=1): ...
    def _draw_aaline(self, color, start, end, width=1): ...
    def _draw_rect(self, color, rect, width=0, br=-1, c1=-1, c2=-1, c3=-1, c4=-1): ...
    def _draw_circle(
        self,
        antialias,
        color,
        center,
        radius,
        width=0,
        c1=False,
        c2=False,
        c3=False,
        c4=False,
    ): ...
    def _draw_poly(self, color, points, width=0, rect=None): ...
    def _draw_ellipse(self, color, rect, outline=0): ...
    def _get_image(
        self, surface, old_source=None
    ) -> pgvideo.Texture | pygame.Surface: ...
    def _blit(self, source, dest, special_flags=0): ...
    def _clear(self, color, window): ...
    def _flip(self, window): ...
    def _start(self): ...
    def _end(self): ...


class SurfaceCanva(_AbstractCanva):
    backend = "surface"

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self._offset = pygame.Vector2()

    @property
    def surface(self):
        return self._surface

    @surface.setter
    def surface(self, value: pygame.Surface):
        self._surface = value
        self._rect = value.get_rect()

    def _get_clip(self) -> pygame.Rect:
        return self._surface.get_clip()

    def _set_clip(self, rect: pygame.Rect):
        self._surface.set_clip(rect)

    def _draw_line(self, color, start, end, width=1):
        pygame.draw.line(self._surface, color, start, end, width)

    def _draw_aaline(self, color, start, end, width=1):
        if pygame.vernum < (2, 5, 6):
            pygame.draw.aaline(self._surface, color, start, end)
        else:
            pygame.draw.aaline(self._surface, color, start, end, width)

    def _draw_rect(self, color, rect, width=0, br=-1, c1=-1, c2=-1, c3=-1, c4=-1):
        pygame.draw.rect(self._surface, color, rect, width, br, c1, c2, c3, c4)

    def _draw_circle(
        self,
        antialias,
        color,
        center,
        radius,
        width=0,
        c1=False,
        c2=False,
        c3=False,
        c4=False,
    ):
        (pygame.draw.aacircle if antialias else pygame.draw.circle)(
            self._surface, color, center, radius, width, c1, c2, c3, c4
        )

    def _draw_poly(self, color, points, width=0, rect=None):
        pygame.draw.polygon(self._surface, color, points, width)

    def _draw_ellipse(self, color, rect, width=0):
        pygame.draw.ellipse(self._surface, color, rect, width)

    def _get_image(self, surface, old=None):
        return surface

    def _blit(self, source, dest, special_flags=0):
        self._surface.blit(source, dest, special_flags=special_flags)

    def _clear(self, color, window):
        window.get_surface().fill(color)

    def _flip(self, window):
        window.flip()


class RendererCanva(_AbstractCanva):
    backend = "renderer"

    def __init__(self, renderer: pgvideo.Renderer, shape_cache_lifetime: int = 1000):
        self.renderer = renderer
        self.shape_cache_lifetime = shape_cache_lifetime
        self._offset = pygame.Vector2()
        self._shape_cache = {}

    @property
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, value: pgvideo.Renderer):
        self._renderer = value
        self._rect = value.get_viewport()
        self._topleft = pygame.Vector2(self._rect.topleft)

    @property
    def offset(self):
        return pygame.Vector2()

    def _get_clip(self) -> pygame.Rect:
        return self._renderer.get_viewport()

    def _set_clip(self, rect: pygame.Rect):
        self._renderer.set_viewport(rect)
        self._topleft = pygame.Vector2(rect.topleft)

    def _get_image(self, surface, old=None):
        if (
            old is not None
            and old.width == surface.width
            and old.height == surface.height
            and old.renderer == self._renderer
        ):
            old.update(surface)
            return old
        return pgvideo.Texture.from_surface(self._renderer, surface)

    def _blit(self, source, dest, special_flags=0):
        if not isinstance(source, pgvideo.Texture):
            return
        if source.renderer is not self._renderer:
            return
        try:
            dest = pygame.Rect(dest)
        except TypeError:
            dest = pygame.Rect(dest, (source.width, source.height))
        dest.topleft -= self._topleft
        try:
            self._renderer.blit(source, dest, special_flags=special_flags)
        except Exception as e:
            print(e, source)

    def _draw_line(self, color, start, end, width=1):
        self._renderer.draw_color = color
        offset_start = start - self._topleft
        offset_end = end - self._topleft
        if width == 1:
            self._renderer.draw_line(offset_start, offset_end)
        else:
            dx = abs(end[0] - start[0])
            dy = abs(end[1] - start[1])
            for i in range(width):
                offset = i - width // 2
                if dx >= dy:
                    offset = (0, offset)
                else:
                    offset = (offset, 0)
                self._renderer.draw_line(offset_start + offset, offset_end + offset)

    _draw_aaline = _draw_line

    def _draw_rect(self, color, rect, width=0, br=-1, c1=-1, c2=-1, c3=-1, c4=-1):
        r = pygame.Rect(rect)
        r.topleft -= self._topleft
        if br <= 0 and c1 == -1 and c2 == -1 and c3 == -1 and c4 == -1:
            self._renderer.draw_color = color
            if width == 0:
                self._renderer.fill_rect(r)
            elif width == 1:
                self._renderer.draw_rect(r)
            elif width > 1:
                self._renderer.fill_rect((r.x, r.y, width, r.h))
                self._renderer.fill_rect((r.x, r.y, r.w, width))
                self._renderer.fill_rect((r.right - width, r.y, width, r.h))
                self._renderer.fill_rect((r.x, r.bottom - width, r.w, width))
        else:
            cache_key = f"{color}_{r.w}_{r.h}_{width}_{br}_{c1}_{c2}_{c3}_{c4}"
            now = pygame.time.get_ticks()
            if cache_key in self._shape_cache:
                texture, last = self._shape_cache[cache_key]
            else:
                surf = pygame.Surface(r.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    surf, color, ((0, 0), r.size), width, br, c1, c2, c3, c4
                )
                texture = pgvideo.Texture.from_surface(self._renderer, surf)
            if texture.renderer is not self._renderer:
                if cache_key in self._shape_cache:
                    del self._shape_cache[cache_key]
                return
            self._shape_cache[cache_key] = (texture, now)
            self._renderer.blit(texture, r)

    def _draw_circle(
        self,
        antialias,
        color,
        center,
        radius,
        width=0,
        c1=False,
        c2=False,
        c3=False,
        c4=False,
    ):
        cache_key = f"{antialias}_{color}_{radius}_{width}_{c1}_{c2}_{c3}_{c4}"
        now = pygame.time.get_ticks()
        if cache_key in self._shape_cache:
            texture, last = self._shape_cache[cache_key]
        else:
            surf = pygame.Surface((radius * 2 + 1, radius * 2 + 1), pygame.SRCALPHA)
            (pygame.draw.aacircle if antialias else pygame.draw.circle)(
                surf, color, (radius, radius), radius, width, c1, c2, c3, c4
            )
            texture = pgvideo.Texture.from_surface(self._renderer, surf)
        if texture.renderer is not self._renderer:
            if cache_key in self._shape_cache:
                del self._shape_cache[cache_key]
            return
        self._shape_cache[cache_key] = (texture, now)
        self._renderer.blit(
            texture,
            pygame.Rect(
                center[0] - radius - self._topleft.x,
                center[1] - radius - self._topleft.y,
                radius * 2,
                radius * 2,
            ),
        )

    def _draw_ellipse(self, color, rect, outline=0):
        r = pygame.Rect(rect)
        r.topleft -= self._topleft
        cache_key = f"{color}_{r.w}_{r.h}_{outline}"
        now = pygame.time.get_ticks()
        if cache_key in self._shape_cache:
            texture, last = self._shape_cache[cache_key]
        else:
            surf = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.ellipse(surf, color, (0, 0, r.w, r.h), outline)
            texture = pgvideo.Texture.from_surface(self._renderer, surf)
        if texture.renderer is not self._renderer:
            if cache_key in self._shape_cache:
                del self._shape_cache[cache_key]
            return
        self._shape_cache[cache_key] = (texture, now)
        self._renderer.blit(
            texture,
            r,
        )

    def _draw_poly(self, color, points, width=0, rect=None):
        if rect is None:
            return
        r = pygame.Rect(rect)
        r.topleft -= self._topleft
        cache_key = f"{color}_{points}_{width}"
        now = pygame.time.get_ticks()
        if cache_key in self._shape_cache:
            texture, last = self._shape_cache[cache_key]
        else:
            surf = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.polygon(surf, color, points, width)
            texture = pgvideo.Texture.from_surface(self._renderer, surf)
        if texture.renderer is not self._renderer:
            if cache_key in self._shape_cache:
                del self._shape_cache[cache_key]
            return
        self._shape_cache[cache_key] = (texture, now)
        self._renderer.blit(
            texture,
            r,
        )

    def _clear(self, color, window):
        self._renderer.draw_color = color
        self._renderer.clear()

    def _flip(self, window):
        self._renderer.present()

    def _start(self):
        self._rect = self._renderer.get_viewport()
        self._topleft = pygame.Vector2(self._rect.topleft)
        for name, (shape, last) in list(self._shape_cache.items()):
            if pygame.time.get_ticks() - last >= self.shape_cache_lifetime:
                del self._shape_cache[name]

    def _end(self):
        self._renderer.set_viewport(None)
