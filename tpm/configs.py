
import typing
from typing import Dict, List, Optional, ClassVar, Self

import mcdreforged.api.all as MCDR

from kpi.config import *
from kpi.utils import LazyData
from .utils import *

__all__ = [
	'MSG_ID', 'BIG_BLOCK_BEFOR', 'BIG_BLOCK_AFTER',
	'TPMConfig', 'get_config',
	'WarpPoint', 'WarpPoints', 'Category', 'Categories',
	'init'
]

MSG_ID = MCDR.RText('[TPM]', color=MCDR.RColor.light_purple)
BIG_BLOCK_BEFOR = LazyData(lambda data:
	MCDR.RText('------------ {0} v{1} ::::'.format(data.name, data.version), color=MCDR.RColor.gold))
BIG_BLOCK_AFTER = LazyData(lambda data:
	MCDR.RText(':::: {0} v{1} ============'.format(data.name, data.version), color=MCDR.RColor.gold))

class TPMConfig(Config, msg_id=MSG_ID):
	# 0:guest 1:user 2:helper 3:admin 4:owner
	class minimum_permission_level(JSONObject):
		posc: int     = 2
		posd: int     = 2
		ask: int     = 1
		askhere: int = 1
		accept: int  = 1
		confirm: int = 1
		reject: int  = 0
		cancel: int  = 0
		warp: int    = 1

		warp_set: int    = 2
		warp_addhere: int    = 2
		warp_remove: int = 1
		warp_config: int = 3
		warp_list: int = 1
		warp_search: int = 1
		warp_rename: int = 1
		warp_disown: int = 1
		warp_alias: int = 1
		warp_rmalias: int = 1

		category_add: int = 1
		category_remove: int = 1
		category_list: int = 1
		category_listc: int = 1
		category_search: int = 1
		category_searchc: int = 1
		category_padd: int = 2
		category_paddhere: int = 2
		category_rename: int = 1
		category_redef: int = 1
		category_premove: int = 1
		category_pmove: int = 1
		category_tag: int = 1
		category_rmtag: int = 1
		category_config: int = 3

	teleport_cooldown: int = 60 # in seconds
	teleport_expiration: int = 10 # in seconds
	teleport_commands: List[str] = [
		'say Teleporting {src} to {dst} ...',
		'tp {src} {dst}',
	]
	teleport_xyz_command: str = 'tp {name} {x} {y} {z}'
	teleport_dim_xyz_command: str = 'execute in {dimension} run tp {name} {x} {y} {z}'
	enable_wrap: bool = True
	max_categories: int = 128
	max_categories_per_player: int = 8

class WarpPoint(JSONObject):
	x: float = 0.0
	y: float = 0.0
	z: float = 0.0
	dimension: str = "minecraft:overworld"
	creator: str = "nobody"
	name: str = "warppoint.name"
	permission: int = 1
	category: str = ''  # legacy compatibility; manual tags are stored in categories.json
	alias: str = ''
	isalias: bool = False

class Category(JSONObject):
	name: str = "category.name"
	prefix: str = "other"
	creator: str = "nobody"
	permission: int = 1


@typing.final
class Categories(JSONStorage):
	_instance: ClassVar[Optional[Self]] = None

	max_categories: int = 128
	categories: List[Category] = []
	tags: Dict[str, list[str]] = {}

	@classmethod
	def instance(cls) -> Optional[Self]:
		return cls._instance

	def _category_items(self) -> list[Category]:
		# KPI 1.5.4 has a broken JSONObject.__iter__ implementation.
		# Always access the JSON field directly so category operations do not
		# accidentally invoke JSONObject.__iter__.
		value = vars(self).get('categories', [])
		return value if isinstance(value, list) else []

	def _tags(self) -> dict[str, list[str]]:
		value = vars(self).get('tags', {})
		if not isinstance(value, dict):
			return {}

		# Normalize the persisted representation in-place. Older versions used
		# {point: "category"}; the current format is {point: ["category", ...]}.
		changed = False
		for key in list(value.keys()):
			raw = value[key]
			if isinstance(raw, str):
				value[key] = [raw]
				changed = True
			elif isinstance(raw, list):
				clean = []
				for category in raw:
					if isinstance(category, str) and category not in clean:
						clean.append(category)
				if clean != raw:
					value[key] = clean
					changed = True
			else:
				del value[key]
				changed = True
		if changed:
			self.save()
		return value

	def get_tags(self, point_name: str) -> list[str]:
		name = point_name.lower()
		for key, categories in self._tags().items():
			if str(key).lower() == name:
				return list(categories)
		return []

	def get_tag(self, point_name: str) -> str:
		# Backward-compatible helper: return the first manual tag, if any.
		tags = self.get_tags(point_name)
		return tags[0] if tags else ''

	def set_tag(self, point_name: str, category: str):
		tags = self._tags()
		# Keep point names normalized so renames/removals are case-insensitive.
		existing_key = point_name
		for key in list(tags.keys()):
			if str(key).lower() == point_name.lower():
				existing_key = key
				break
		if existing_key != point_name:
			current = tags.pop(existing_key)
		else:
			current = tags.get(point_name, [])
		if not isinstance(current, list):
			current = [current] if isinstance(current, str) else []
		if category not in current:
			current.append(category)
		tags[point_name] = current
		self.save()

	def remove_tag(self, point_name: str, category: str | None = None):
		tags = self._tags()
		changed = False
		for key in list(tags.keys()):
			if str(key).lower() != point_name.lower():
				continue
			if category is None:
				del tags[key]
				changed = True
				continue
			remaining = [c for c in tags[key] if str(c).lower() != category.lower()]
			if remaining != tags[key]:
				changed = True
				if remaining:
					tags[key] = remaining
				else:
					del tags[key]
		if changed:
			self.save()
		return changed

	def remove_tags_for_category(self, category: str):
		tags = self._tags()
		category = category.lower()
		changed = False
		for key in list(tags.keys()):
			remaining = [c for c in tags[key] if str(c).lower() != category]
			if remaining != tags[key]:
				changed = True
				if remaining:
					tags[key] = remaining
				else:
					del tags[key]
		if changed:
			self.save()

	def rename_tags_category(self, old: str, new: str):
		tags = self._tags()
		old = old.lower()
		changed = False
		for key in list(tags.keys()):
			updated = [new if str(c).lower() == old else c for c in tags[key]]
			# Avoid duplicates if the renamed category was already present.
			deduped = []
			for category in updated:
				if category not in deduped:
					deduped.append(category)
			if deduped != tags[key]:
				tags[key] = deduped
				changed = True
		if changed:
			self.save()

	def migrate_legacy_tags(self, points):
		# Migrate the temporary category field used by older builds into the
		# persistent categories.json/tags mapping.
		tags = self._tags()
		changed_tags = False
		changed_points = False
		for point in points.warp_points:
			legacy = getattr(point, 'category', '')
			if legacy:
				if legacy not in self.get_tags(point.name):
					# Keep any already-persisted multi-category tags and append
					# the legacy tag instead of overwriting them.
					tags.setdefault(point.name, []).append(legacy)
					changed_tags = True
				try:
					delattr(point, 'category')
				except AttributeError:
					pass
				changed_points = True
		if changed_tags:
			self.save()
		if changed_points:
			points.save()

	@property
	def categories_count(self) -> int:
		return len(self._category_items())

	def get_player_category_used(self, player: str) -> int:
		player = player.lower()
		return sum(1 for c in self._category_items() if c.creator.lower() == player)

	def get_category(self, name: str) -> Category | None:
		name = name.lower()
		for c in self._category_items():
			if c.name.lower() == name:
				return c
		return None

	def get_category_by_prefix(self, prefix: str) -> Category | None:
		prefix = prefix.lower().rstrip(':')
		for c in self._category_items():
			if c.prefix.lower().rstrip(':') == prefix:
				return c
		return None

	def set_category(self, category: Category):
		items = self._category_items()
		name = category.name.lower()
		for i, c in enumerate(items):
			if c.name.lower() == name:
				items[i] = category
				break
		else:
			items.append(category)
		self.save()

	def remove_category(self, name: str) -> Category | None:
		items = self._category_items()
		name = name.lower()
		for i, c in enumerate(items):
			if c.name.lower() == name:
				items.pop(i)
				self.save()
				return c
		return None

@typing.final
class WarpPoints(JSONStorage):
	_instance: ClassVar[Optional[Self]] = None

	max_warp_points: int = 8192
	max_warp_points_per_player: int = 8
	warp_points: List[WarpPoint] = []

	@classmethod
	def instance(cls) -> Optional[Self]:
		return cls._instance

	@property
	def points_count(self) -> int:
		return len(self.warp_points)

	def get_player_point_used(self, player: str) -> int:
		count = 0
		player = player.lower()
		for p in self.warp_points:
			if p.creator.lower() == player:
				count = count + 1
		return count

	def get_point(self, name: str) -> WarpPoint | None:
		name = name.lower()
		for p in self.warp_points:
			if p.name.lower() == name:
				return p
		return None

	def set_point(self, point: WarpPoint):
		name = point.name.lower()
		for i, p in enumerate(self.warp_points):
			if p.name.lower() == name:
				self.warp_points[i] = point
				break
		else:
			self.warp_points.append(point)
		self.save()

	def remove_point(self, name: str) -> WarpPoint | None:
		name = name.lower()
		for i, p in enumerate(self.warp_points):
			if p.name.lower() == name:
				self.warp_points.pop(i)
				self.save()
				# Keep categories.json tags in sync with points.json.
				# All warp-point deletion paths go through this method, so a
				# manual category tag can never be left behind as stale data.
				try:
					Categories.instance().remove_tag(p.name)
				except (AttributeError, RuntimeError):
					# Categories may not have been initialized yet during startup.
					pass
				return p
		return None

def get_config() -> TPMConfig:
	return TPMConfig.instance()

def init(server: MCDR.PluginServerInterface):
	global BIG_BLOCK_BEFOR, BIG_BLOCK_AFTER
	metadata = server.get_self_metadata()
	LazyData.load(BIG_BLOCK_BEFOR, metadata)
	LazyData.load(BIG_BLOCK_AFTER, metadata)
	TPMConfig.init_instance(server, load_after_init=True).save()
	WarpPoints._instance = WarpPoints(server, 'points.json', sync_update=True, load_after_init=True)
	Categories._instance = Categories(server, 'categories.json', sync_update=True, load_after_init=True)
	Categories._instance.migrate_legacy_tags(WarpPoints._instance)
