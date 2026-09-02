 
import time
from typing import Callable, TypeVar
import nbtlib as snbt
import math

import mcdreforged.api.all as MCDR

from kpi.command import *
from kpi.utils import get_server_instance

from .configs import *
from .utils import *
from .api import *

Prefix = '!!tp'
AlternativePrefix = '!!tpm'
TpaPrefix = '!!tpa'
TphPrefix = '!!tph'
WarpPrefix = '!!warp'

page_size = 16 # default

def register(server: MCDR.PluginServerInterface):
	cfg = get_config()
	points = WarpPoints.instance()
	assert points

	cmd = Commands(Prefix, config=cfg, points=points)
	cmd.register_to(server)

	server.register_command(
		MCDR.Literal(AlternativePrefix).redirects(cmd.node))

	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(TpaPrefix), 'ask')).
		redirects(Commands.ask.node))
	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(TphPrefix), 'askhere')).
			redirects(Commands.askhere.node))
	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(WarpPrefix), 'warp')).
			redirects(Commands.warp.node))
	server.register_help_message(TpaPrefix, 'Teleport to player')
	server.register_help_message(TphPrefix, 'Teleport player to you')
	server.register_help_message(WarpPrefix, 'Warp to warp point')

Self = TypeVar("Self", bound="Commands")

#global__tpspb_map: dict[str, list[str, float]] = {}

class Commands(PermCommandSet):
	Prefix = Prefix
	HelpMessage = 'TP manager help message'

	def __init__(self, *args, config: TPMConfig, points: WarpPoints, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = config
		self.__points = points
		self.__tpask_map: dict[str, tuple[Callable, Callable]] = {}
		self.__tpsender_map: dict[str, Callable] = {}
		self.__last_teleports: dict[str, float] = {}

	@property
	def config(self):
		return self.__config

	@property
	def points(self) -> WarpPoints:
		return self.__points

	@property
	def categories(self) -> Categories:
		return Categories.instance()

	def _category_list(self) -> list[Category]:
		"""Return persisted categories without invoking KPI 1.5.4's broken iterator."""
		storage = Categories.instance()
		if storage is None:
			return []
		value = vars(storage).get('categories', [])
		return value if isinstance(value, list) else []

	def has_permission(self, src: MCDR.CommandSource, literal: str) -> bool:
		return self.config.has_permission(src, literal)

	def help(self, source: MCDR.CommandSource):
		send_message(source, BIG_BLOCK_BEFOR, tr('help_msg', Prefix, tpa=TpaPrefix, tph=TphPrefix), BIG_BLOCK_AFTER, sep='\n')

	@Literal('posc')
	@player_only
	def tpposc(self, source: MCDR.PlayerCommandSource, x: str, y: str, z: str):
		server = source.get_server()
		player = source.player
		cooldown = self.config.teleport_cooldown
		if cooldown > 0:
			now = time.time()
			remain = self.__last_teleports.get(player, 0) + cooldown - now
			if remain > 0:
				send_message(source, MSG_ID, MCDR.RText(tr('ask.cooldown', round(remain)), color=MCDR.RColor.red))
				return
			self.__last_teleports[player] = now

		#if x == "~": x = float(server.rcon_query('data get entity {} Pos[0]'.format(player)).split(": ")[-1][:-1])
		#if y == "~":  y = float(server.rcon_query('data get entity {} Pos[1]'.format(player)).split(": ")[-1][:-1])
		#if z == "~": z = float(server.rcon_query('data get entity {} Pos[2]'.format(player)).split(": ")[-1][:-1])
		try:
			if(x != '~' and x != '^'):
				float(x)
		except ValueError:
			if(x[0] == '~' or x[0] == '^'):
				try:
					float(x[1:])
				except Exception:
					send_message(source, MSG_ID, MCDR.RText(tr('ask.invalid_position', err='x'), color=MCDR.RColor.red))
					return

		try:
			if(y != '~' and y != '^'):
				float(y)
		except ValueError:
			if(y[0] == '~' or y[0] == '^'):
				try:
					float(y[1:])
				except Exception:
					send_message(source, MSG_ID, MCDR.RText(tr('ask.invalid_position', err='y'), color=MCDR.RColor.red))
					return

		try:
			if(z != '~' and z != '^'):
				float(z)
		except ValueError:
			if(z[0] == '~' or z[0] == '^'):
				try:
					float(z[1:])
				except Exception:
					send_message(source, MSG_ID, MCDR.RText(tr('ask.invalid_position', err='z'), color=MCDR.RColor.red))
					return

		cmd = "execute as %s at %s run tp %s %s %s %s" %(player, player, player, x, y, z)
		server.execute(cmd)

	@Literal('posd')
	@player_only
	def tpposd(self, source: MCDR.PlayerCommandSource, d: str, x: str, y: str, z: str):
		server = source.get_server()
		player = source.player
		cooldown = self.config.teleport_cooldown
		if cooldown > 0:
			now = time.time()
			remain = self.__last_teleports.get(player, 0) + cooldown - now
			if remain > 0:
				send_message(source, MSG_ID, MCDR.RText(tr('ask.cooldown', round(remain)), color=MCDR.RColor.red))
				return
			self.__last_teleports[player] = now

		#if x == "~": x = float(server.rcon_query('data get entity {} Pos[0]'.format(player)).split(": ")[-1][:-1])
		#if y == "~":  y = float(server.rcon_query('data get entity {} Pos[1]'.format(player)).split(": ")[-1][:-1])
		#if z == "~": z = float(server.rcon_query('data get entity {} Pos[2]'.format(player)).split(": ")[-1][:-1])
		
		#cmd = self.config.teleport_dim_xyz_command.format(dimension=d, name=player, x=x, y=y, z=z)

		try:
			if(x != '~' and x != '^'):
				float(x)
		except ValueError:
			if(x[0] == '~' or x[0] == '^'):
				try:
					float(x[1:])
				except Exception:
					send_message(source, MSG_ID, MCDR.RText(tr('ask.invalid_position', err='x'), color=MCDR.RColor.red))
					return

		try:
			if(y != '~' and y != '^'):
				float(y)
		except ValueError:
			if(y[0] == '~' or y[0] == '^'):
				try:
					float(y[1:])
				except Exception:
					send_message(source, MSG_ID, MCDR.RText(tr('ask.invalid_position', err='y'), color=MCDR.RColor.red))
					return

		try:
			if(z != '~' and z != '^'):
				float(z)
		except ValueError:
			if(z[0] == '~' or z[0] == '^'):
				try:
					float(z[1:])
				except Exception:
					send_message(source, MSG_ID, MCDR.RText(tr('ask.invalid_position', err='z'), color=MCDR.RColor.red))
					return

		cmd = "execute in %s run tp %s %d %d %d" % (d, player, x, y ,z)
		server.execute(cmd)

	@Literal('ask')
	@player_only
	def ask(self, source: MCDR.PlayerCommandSource, target: str):
		server = source.get_server()
		name = source.player
		query = server.rcon_query(f"data get entity {target} Tags").split("has the following entity data: ")
		if len(query) > 1:
			nbtdata = snbt.parse_nbt(query[-1])
			is_bot = "BOT" in nbtdata.unpack()
			is_spb = "SPECIAL_BOT" in nbtdata.unpack()
		else:
			is_bot = False
			is_spb = False

		if is_bot or is_spb:
			server.execute(f"tp {name} {target}")
			return
		'''
		if is_spb:
			cttime = time.time()
			global__tpspb_map.update({source, [target, cttime]})
			#send_message(source, MCDR.RText(tr('ask.spb'), color=MCDR.RColor.yellow))
			server.tell(name, f"§c{tr('ask.spb')}")
			return
'''
		if not is_online(target):
			send_message(source, MSG_ID, MCDR.RText(tr('ask.player_not_online', target), color=MCDR.RColor.yellow))
			return

		if not self.register_accept(source, target,
			lambda: self.execute_teleport_commands(server, target, name),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.timeout'), color=MCDR.RColor.red)),
			timeout=self.config.teleport_expiration):
			return
		send_message(source, MSG_ID, tr('ask.sending', target),
			new_command('{} cancel'.format(Prefix), '[{}]'.format(tr('word.cancel')), color=MCDR.RColor.yellow))
		server.tell(target, join_rtext(MSG_ID, tr('ask.request_to', name),
			new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
			new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
		))

	def execute_teleport_commands(self, server: MCDR.ServerInterface, target: str, name: str):
		for c in self.config.teleport_commands:
			server.execute(c.format(src=name, dst=target))

	@Literal(['askhere', 'here'])
	@player_only
	def askhere(self, source: MCDR.PlayerCommandSource, target: str):
		server = source.get_server()
		name = source.player
		if not is_online(target):
			send_message(source, MSG_ID, MCDR.RText(tr('ask.player_not_online', target), color=MCDR.RColor.yellow))
		if not self.register_accept(source, target,
			lambda: self.execute_teleport_commands(server, name, target),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.timeout'), color=MCDR.RColor.red)),
			timeout=self.config.teleport_expiration):
			return
		send_message(source, MSG_ID, tr('ask.sending', target),
			new_command('{} cancel'.format(Prefix), '[{}]'.format(tr('word.cancel')), color=MCDR.RColor.yellow))
		server.tell(target, join_rtext(MSG_ID, tr('ask.request_from', name),
			new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
			new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
		))

	'''
	@Literal("confirm")
	@player_only
	def confirmcmd(source: MCDR.PlayerCommandSource):
		server = source.get_server()
		name = source.player

		if name in global__tpspb_map:
			if global__tpspb_map[name][1] + 60.0 >= time.time():
				server.execute(f"tp {name} {global__tpspb_map[name][0]}")
				global__tpspb_map.pop(name)
				return
			else:
				send_message(source, MCDR.RText(tr('ask.timeout'), color=MCDR.RColor.red))
				global__tpspb_map.pop(name)
				return
		else:
			send_message(source, MCDR.RText(tr('ask.unknownrequest'), color=MCDR.RColor.red))
			return
	'''

	@Literal(['accept', 'acc'])
	@player_only
	def accept(self, source: MCDR.PlayerCommandSource):
		cbs = self.__tpask_map.pop(source.player.lower(), None)
		if cbs is None:
			send_message(source, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))
			return
		cbs[0](source)

	@Literal(['reject', 'r'])
	@player_only
	def reject(self, source: MCDR.PlayerCommandSource):
		cbs = self.__tpask_map.pop(source.player.lower(), None)
		if cbs is None:
			send_message(source, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))
			return
		cbs[1](source)

	@Literal(['cancel', 'c'])
	@player_only
	def cancel(self, source: MCDR.PlayerCommandSource):
		cb = self.__tpsender_map.pop(source.player.lower(), None)
		if cb is None:
			send_message(source, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))
			return
		cb(source)

	def _has_warp_permission(self, source: MCDR.CommandSource, point: WarpPoint) -> bool:
		return source.has_permission(point.permission) or (isinstance(source, MCDR.PlayerCommandSource) and source.player.lower() == point.creator.lower())

	@Literal(['warp', 'w'])
	@player_only
	def warp(self, source: MCDR.PlayerCommandSource, name: str):
		server = source.get_server()
		if not self.config.enable_wrap:
			send_message(source, MCDR.RText(tr('warp.disabled'), color=MCDR.RColor.red))
			return
		
		point = self.points.get_point(name)

		if point is None:
			send_message(source, MCDR.RText(tr('warp.points.not_exists', name), color=MCDR.RColor.red))
			return

		while point.isalias:
			_alias = point.alias
			point = self.points.get_point(_alias)
			if point is None: # or not source.has_permission(point.permission):
				send_message(source, MCDR.RText(tr('warp.points.not_exists', _alias), color=MCDR.RColor.red))
				return
			
		if not self._has_warp_permission(source, point):
			send_message(source, MCDR.RText(tr('warp.points.no_permission'), color=MCDR.RColor.red))
			return
		send_message(source, MCDR.RText(tr('warp.teleporting', name=point.name), color=MCDR.RColor.light_purple))
		cmd = self.config.teleport_dim_xyz_command.format(name=source.player, x=point.x, y=point.y, z=point.z, dimension=point.dimension)
		server.execute(cmd)

	@Literal(['categories', 'category', 'cats'])
	class categories(PermCommandSet):
		def default(self, source: MCDR.CommandSource):
			# Match the existing warps command-set default invocation.
			self.listc(self, source)

		def has_permission(self, src: MCDR.CommandSource, literal: str) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset.config.has_permission(src, 'category_' + literal)

		def has_force_permission(self, src: MCDR.CommandSource) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset.config.has_permission(src, 'category_config')

		@property
		def points(self) -> WarpPoints:
			assert isinstance(self.rootset, Commands)
			return self.rootset.points

		@property
		def categories(self) -> Categories:
			return Categories.instance()

		def _category(self, name: str) -> Category | None:
			return self.categories.get_category(name)

		def _has_category_permission(self, source: MCDR.CommandSource, category: Category) -> bool:
			assert isinstance(self.rootset, Commands)
			return source.has_permission(category.permission) or (
				isinstance(source, MCDR.PlayerCommandSource) and source.player.lower() == category.creator.lower())

		def _display_point(self, source: MCDR.CommandSource, point: WarpPoint):
			if not point.isalias:
				send_message(source, tr('warp.point', x=round(point.x, 2), y=round(point.y, 2),
					z=round(point.z, 2), dimension=point.dimension, name=point.name, c=point.creator))
			else:
				send_message(source, tr('warp.pointalias', name=point.name, c=point.creator, to=point.alias))

		def _is_in_category(self, point: WarpPoint, category: Category) -> bool:
			# Explicit tags stored in categories.json override prefix-based classification.
			# A warp point may be manually assigned to multiple categories.
			point_categories = self.categories.get_tags(point.name)
			if point_categories:
				return any(c.lower() == category.name.lower() for c in point_categories)

			# An untagged alias belongs to the category of its final target. Follow
			# alias chains until a non-alias point is reached.
			current = point
			visited: set[str] = set()
			while current.isalias:
				key = current.name.lower()
				if key in visited:
					return False
				visited.add(key)
				target = self.points.get_point(current.alias)
				if target is None:
					return False
				current = target
			return current.name.lower().startswith(category.prefix.lower().rstrip(':') + ':')

		def _resolve_alias(self, point: WarpPoint) -> WarpPoint | None:
			current = point
			visited: set[str] = set()
			while current.isalias:
				key = current.name.lower()
				if key in visited:
					return None
				visited.add(key)
				current = self.points.get_point(current.alias)
				if current is None:
					return None
			return current

		def _other_points(self) -> list[WarpPoint]:
			result = []
			categories = self.rootset._category_list()
			for point in self.points.warp_points:
				# Explicitly tagged points are never part of the built-in `other`
				# category as long as at least one tag refers to an existing category.
				point_categories = self.categories.get_tags(point.name)
				if point_categories:
					if any(tag.lower() == category.name.lower() for tag in point_categories for category in categories):
						continue
				# For untagged aliases, category membership is determined by the final target.
				resolved = self._resolve_alias(point)
				check = resolved if resolved is not None else point
				if not any(self._is_in_category(check, category) for category in categories):
					result.append(point)
			return result

		def _get_category_points(self, category: str) -> tuple[Category, list[WarpPoint]] | None:
			c = self._category(category)
			if c is not None:
				return c, [p for p in self.points.warp_points if self._is_in_category(p, c)]
			if category.lower() == 'other':
				return Category(name='other', prefix='', creator='**builtin', permission=0), self._other_points()
			return None

		def _find_category_point(self, category: Category, name: str) -> WarpPoint | None:
			# Accept either the full generated name (prefix:name) or the point
			# name as used by category commands.
			full_name = category.prefix.rstrip(':') + ':' + name
			point = self.points.get_point(name)
			if point is not None and self._is_in_category(point, category):
				return point
			point = self.points.get_point(full_name)
			if point is not None and self._is_in_category(point, category):
				return point
			return None

		def _paginate(self, source: MCDR.CommandSource, objects: list, page: int, display):
			global page_size
			if page <= 0:
				send_message(source, MCDR.RText(tr('warp.mustlargerthanzero'), color=MCDR.RColor.red))
				return
			objects.sort(key=lambda obj: obj.name.upper())
			start_position = (page - 1) * page_size
			end_position = page * page_size
			total = math.ceil(len(objects) / page_size)
			if start_position > len(objects):
				send_message(source, MCDR.RText(tr('warp.outofpages', c=page, t=total), color=MCDR.RColor.red))
				return
			send_message(source, BIG_BLOCK_BEFOR)
			send_message(source, MCDR.RText(tr('category.pages', c=page, t=total), color=MCDR.RColor.dark_green))
			for obj in objects[start_position:end_position]:
				display(source, obj)
			send_message(source, BIG_BLOCK_AFTER)

		@Literal('add')
		def add(self, source: MCDR.CommandSource, name: str, prefix: str):
			if not prefix or ':' in prefix:
				send_message(source, MCDR.RText(tr('category.invalid_prefix'), color=MCDR.RColor.red))
				return
			if len(name) > 32 or len(prefix) > 31:
				send_message(source, MCDR.RText(tr('category.overlength'), color=MCDR.RColor.red))
				return
			if name.lower() == 'other':
				send_message(source, MCDR.RText(tr('category.reserved_name'), color=MCDR.RColor.red))
				return
			if self._category(name) is not None:
				send_message(source, MCDR.RText(tr('category.exists', name), color=MCDR.RColor.red))
				return
			if self.categories.get_category_by_prefix(prefix) is not None:
				send_message(source, MCDR.RText(tr('category.prefix_exists', prefix), color=MCDR.RColor.red))
				return
			if self.categories.categories_count >= self.rootset.config.max_categories:
				send_message(source, MCDR.RText(tr('category.full', self.rootset.config.max_categories), color=MCDR.RColor.red))
				return
			if isinstance(source, MCDR.PlayerCommandSource):
				used = self.categories.get_player_category_used(source.player)
				if used >= self.rootset.config.max_categories_per_player and not self.has_force_permission(source):
					send_message(source, MCDR.RText(tr('category.full_per_player', count=used, limit=self.rootset.config.max_categories_per_player), color=MCDR.RColor.red))
					return
			creator = source.player if isinstance(source, MCDR.PlayerCommandSource) else ''
			self.categories.set_category(Category(name=name, prefix=prefix, creator=creator, permission=1))
			send_message(source, MCDR.RText(tr('category.created', name=name, prefix=prefix), color=MCDR.RColor.green), log=True)

		@Literal(['remove', 'rm'])
		def remove(self, source: MCDR.CommandSource, name: str):
			category = self._category(name)
			if category is None:
				send_message(source, MCDR.RText(tr('category.not_exists', name), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, category) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			self.categories.remove_category(category.name)
			self.categories.remove_tags_for_category(category.name)
			send_message(source, MCDR.RText(tr('category.removed', name=category.name), color=MCDR.RColor.gold), log=True)

		@Literal(['list', 'l'])
		def list(self, source: MCDR.CommandSource, category: str, page: int = 1):
			result = self._get_category_points(category)
			if result is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			cat, points = result
			points = [p for p in points if self.rootset._has_warp_permission(source, p)]
			self._paginate(source, points, page, self._display_point)

		@Literal(['listc', 'lc'])
		def listc(self, source: MCDR.CommandSource, page: int = 1):
			objects = list(self.rootset._category_list())
			if self._other_points() and self._category('other') is None:
				objects.append(Category(name='other', prefix='', creator='**builtin', permission=0))
			self._paginate(source, objects, page, lambda src, c: send_message(src, tr('category.item', name=c.name, prefix=(c.prefix + ':' if c.prefix else ''), creator=(tr('category.builtin') if c.creator == '**builtin' else c.creator))))

		@Literal(['searchc', 'sc'])
		def searchc(self, source: MCDR.CommandSource, pattern: str, page: int = 1):
			objects = [c for c in self.rootset._category_list() if pattern.lower() in c.name.lower() or pattern.lower() in c.prefix.lower()]
			if pattern.lower() in 'other' and self._other_points() and self._category('other') is None:
				objects.append(Category(name='other', prefix='', creator='**builtin', permission=0))
			self._paginate(source, objects, page, lambda src, c: send_message(src, tr('category.item', name=c.name, prefix=(c.prefix + ':' if c.prefix else ''), creator=(tr('category.builtin') if c.creator == '**builtin' else c.creator))))

		@Literal(['search', 'se'])
		def search(self, source: MCDR.CommandSource, category: str, pattern: str, page: int = 1):
			result = self._get_category_points(category)
			if result is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			_, points = result
			points = [p for p in points if self.rootset._has_warp_permission(source, p) and pattern.lower() in p.name.lower()]
			self._paginate(source, points, page, self._display_point)

		def _validate_category_point(self, source: MCDR.CommandSource, category: Category, full_name: str) -> WarpPoint | None:
			if len(full_name) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return None
			point = self.points.get_point(full_name)
			if point is None:
				if self.points.points_count >= self.points.max_warp_points:
					send_message(source, MCDR.RText(tr('warp.points.full'), color=MCDR.RColor.red))
					return None
				if isinstance(source, MCDR.PlayerCommandSource) and not self.has_force_permission(source):
					used = self.points.get_player_point_used(source.player)
					if used >= self.points.max_warp_points_per_player:
						send_message(source, MCDR.RText(tr('warp.points.full_per_player', count=used, limit=self.points.max_warp_points_per_player), color=MCDR.RColor.red))
						return None
			elif not self.rootset._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.points.exists'), color=MCDR.RColor.red))
				return None
			return point

		def _save_category_point(self, source: MCDR.CommandSource, category: Category, name: str, x: float, y: float, z: float, dimension: str):
			full_name = category.prefix.rstrip(':') + ':' + name
			if len(full_name) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return
			point = self.points.get_point(full_name)
			if point is None:
				if self.points.points_count >= self.points.max_warp_points:
					send_message(source, MCDR.RText(tr('warp.points.full'), color=MCDR.RColor.red))
					return
				if isinstance(source, MCDR.PlayerCommandSource) and not self.has_force_permission(source):
					used = self.points.get_player_point_used(source.player)
					if used >= self.points.max_warp_points_per_player:
						send_message(source, MCDR.RText(tr('warp.points.full_per_player', count=used, limit=self.points.max_warp_points_per_player), color=MCDR.RColor.red))
						return
			elif not self.rootset._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			self.points.set_point(WarpPoint(x=float(x), y=float(y), z=float(z), dimension=dimension, name=full_name,
				creator=source.player if isinstance(source, MCDR.PlayerCommandSource) else '', permission=1))
			send_message(source, MCDR.RText(tr('warp.created', full_name) if point is None else tr('warp.updated', point.name), color=MCDR.RColor.green), log=True)

		@Literal('padd')
		def padd(self, source: MCDR.CommandSource, category: str, name: str, x: float, y: float, z: float, dimension: str):
			cat = self._category(category)
			if cat is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, cat) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			self._save_category_point(source, cat, name, x, y, z, dimension)

		@Literal('paddhere')
		@player_only
		def paddhere(self, source: MCDR.PlayerCommandSource, category: str, name: str):
			cat = self._category(category)
			if cat is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, cat) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			server = source.get_server()
			player = source.player
			x = float(server.rcon_query('data get entity {} Pos[0]'.format(player)).split(': ')[-1][:-1])
			y = float(server.rcon_query('data get entity {} Pos[1]'.format(player)).split(': ')[-1][:-1])
			z = float(server.rcon_query('data get entity {} Pos[2]'.format(player)).split(': ')[-1][:-1])
			dimension = eval(server.rcon_query('data get entity {} Dimension'.format(player)).split(': ')[-1])
			self._save_category_point(source, cat, name, x, y, z, dimension)

		@Literal('tag')
		def tag(self, source: MCDR.CommandSource, warp_point: str, category: str):
			cat = self._category(category)
			if cat is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, cat) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			point = self.points.get_point(warp_point)
			if point is None:
				send_message(source, MCDR.RText(tr('warp.points.not_exists', warp_point), color=MCDR.RColor.red))
				return
			if not self.rootset._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return
			if any(existing.lower() == cat.name.lower() for existing in self.categories.get_tags(point.name)):
				send_message(source, MCDR.RText(tr('category.point_already_tagged', point=point.name, category=cat.name), color=MCDR.RColor.yellow))
				return
			self.categories.set_tag(point.name, cat.name)
			send_message(source, MCDR.RText(tr('category.point_tagged', point=point.name, category=cat.name), color=MCDR.RColor.gold), log=True)

		@Literal('rmtag')
		def rmtag(self, source: MCDR.CommandSource, warp_point: str):
			point = self.points.get_point(warp_point)
			if point is None:
				send_message(source, MCDR.RText(tr('warp.points.not_exists', warp_point), color=MCDR.RColor.red))
				return
			if not self.rootset._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return
			if not self.categories.get_tags(point.name):
				send_message(source, MCDR.RText(tr('category.point_not_tagged', point=point.name), color=MCDR.RColor.red))
				return
			self.categories.remove_tag(point.name)
			send_message(source, MCDR.RText(tr('category.point_tags_removed', point=point.name), color=MCDR.RColor.gold), log=True)

		@Literal(['premove', 'prm'])
		def premove(self, source: MCDR.CommandSource, category: str, warp_point: str):
			cat = self._category(category)
			if cat is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, cat) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			point = self._find_category_point(cat, warp_point)
			if point is None:
				send_message(source, MCDR.RText(tr('category.point_not_exists', category=cat.name, point=warp_point), color=MCDR.RColor.red))
				return
			if not self.rootset._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return
			self.points.remove_point(point.name)
			send_message(source, MCDR.RText(tr('category.point_removed', point=point.name, category=cat.name), color=MCDR.RColor.gold), log=True)

		@Literal(['pmove', 'pmv'])
		def pmove(self, source: MCDR.CommandSource, category: str, point: str, other_category: str):
			cat = self._category(category)
			other = self._category(other_category)
			if cat is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			if other is None:
				send_message(source, MCDR.RText(tr('category.not_exists', other_category), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, cat) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, other) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			wp = self._find_category_point(cat, point)
			if wp is None:
				send_message(source, MCDR.RText(tr('category.point_not_exists', category=cat.name, point=point), color=MCDR.RColor.red))
				return
			if not self.rootset._has_warp_permission(source, wp) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return
			if wp.name.lower().startswith(cat.prefix.lower().rstrip(':') + ':'):
				point_name = wp.name.split(':', 1)[1]
			else:
				point_name = point.split(':', 1)[1] if ':' in point else point
			new_name = other.prefix.rstrip(':') + ':' + point_name
			if len(new_name) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return
			existing = self.points.get_point(new_name)
			if existing is not None and existing.name.lower() != wp.name.lower():
				send_message(source, MCDR.RText(tr('warp.points.exists', new_name), color=MCDR.RColor.red))
				return
			self.points.remove_point(wp.name)
			self.points.set_point(WarpPoint(x=wp.x, y=wp.y, z=wp.z, dimension=wp.dimension, name=new_name,
				creator=wp.creator, permission=wp.permission, isalias=wp.isalias, alias=wp.alias))
			send_message(source, MCDR.RText(tr('category.point_moved', o=wp.name, n=new_name, category=other.name), color=MCDR.RColor.gold), log=True)

		@Literal(['rename', 're'])
		def rename(self, source: MCDR.CommandSource, old: str, new: str):
			category = self._category(old)
			if category is None:
				send_message(source, MCDR.RText(tr('category.not_exists', old), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, category) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			if new.lower() == 'other' or len(new) > 32:
				send_message(source, MCDR.RText(tr('category.invalid_name'), color=MCDR.RColor.red))
				return
			if self._category(new) is not None and self._category(new).name.lower() != category.name.lower():
				send_message(source, MCDR.RText(tr('category.exists', new), color=MCDR.RColor.red))
				return
			self.categories.remove_category(category.name)
			self.categories.set_category(Category(name=new, prefix=category.prefix, creator=category.creator, permission=category.permission))
			self.categories.rename_tags_category(category.name, new)
			send_message(source, MCDR.RText(tr('category.renamed', o=old, n=new), color=MCDR.RColor.gold), log=True)

		@Literal('redef')
		def redef(self, source: MCDR.CommandSource, category: str, new_prefix: str):
			cat = self._category(category)
			if cat is None:
				send_message(source, MCDR.RText(tr('category.not_exists', category), color=MCDR.RColor.red))
				return
			if not self._has_category_permission(source, cat) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('category.permdenied'), color=MCDR.RColor.red))
				return
			if not new_prefix or ':' in new_prefix or len(new_prefix) > 31:
				send_message(source, MCDR.RText(tr('category.invalid_prefix'), color=MCDR.RColor.red))
				return
			existing = self.categories.get_category_by_prefix(new_prefix)
			if existing is not None and existing.name.lower() != cat.name.lower():
				send_message(source, MCDR.RText(tr('category.prefix_exists', new_prefix), color=MCDR.RColor.red))
				return
			self.categories.set_category(Category(name=cat.name, prefix=new_prefix, creator=cat.creator, permission=cat.permission))
			send_message(source, MCDR.RText(tr('category.redefined', name=cat.name, prefix=new_prefix), color=MCDR.RColor.gold), log=True)

	@Literal(['warps', 'ws'])
	class warps(PermCommandSet):
		def has_permission(self, src: MCDR.CommandSource, literal: str) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset.config.has_permission(src, 'warp_' + literal)

		def has_force_permission(self, src: MCDR.CommandSource) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset.config.has_permission(src, 'warp_config')

		@property
		def points(self) -> WarpPoints:
			assert isinstance(self.rootset, Commands)
			return self.rootset.points

		def _has_warp_permission(self, source: MCDR.CommandSource, point: WarpPoint) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset._has_warp_permission(source, point)

		def default(self, source: MCDR.CommandSource):
			self.list(self, source)

		@Literal(['list', 'l'])
		def list(self: Self, source: MCDR.CommandSource, page: int = 1):
			global page_size

			if page <= 0:
				send_message(source, MCDR.RText(tr('warp.mustlargerthanzero'), color = MCDR.RColor.red))
				return

			points = [p for p in self.points.warp_points if self._has_warp_permission(source, p)]
			points.sort(key=lambda p: p.name.upper())

			counter = 0

			start_position = (page - 1) * page_size
			end_position = page * page_size

			total = math.ceil(len(points) / page_size)

			if(start_position > len(points)):
				send_message(source, MCDR.RText(tr('warp.outofpages', c = page, t = total), color = MCDR.RColor.red))
				return 

			send_message(source, BIG_BLOCK_BEFOR)
			send_message(source, MCDR.RText(tr('warp.pages', c = page, t = total), color = MCDR.RColor.dark_green))
			for p in points:
				if counter < start_position:
					counter += 1
					continue
				if counter >= end_position:
					break
				counter += 1
				if not p.isalias:
					send_message(source, tr('warp.point', x=round(p.x, 2), y=round(p.y, 2), z=round(p.z, 2), dimension=p.dimension, name=p.name, c=p.creator))
				else:
					send_message(source, tr('warp.pointalias', name=p.name, c=p.creator, to=p.alias))
			send_message(source, BIG_BLOCK_AFTER)

		@Literal(["search", "se"])
		def search(self: Self, source: MCDR.CommandSource, pattern: str, page: int = 1):
			global page_size

			if page <= 0:
				send_message(source, MCDR.RText(tr('warp.mustlargerthanzero'), color = MCDR.RColor.red))
				return

			points = [p for p in self.points.warp_points if self._has_warp_permission(source, p)]
			points.sort(key=lambda p: p.name.upper())

			objects: list[WarpPoint] = []
			for p in points:
				if pattern not in p.name: continue
				objects.append(p)

			counter = 0
			
			start_position = (page - 1) * page_size
			end_position = page * page_size
			
			total = math.ceil(len(objects) / page_size)
			
			if(start_position > len(objects)):
				send_message(source, MCDR.RText(tr('warp.outofpages', c = page, t = total), color = MCDR.RColor.red))
				return

			send_message(source, BIG_BLOCK_BEFOR)
			send_message(source, MCDR.RText(tr('warp.pages', c = page, t = total), color = MCDR.RColor.dark_green))
			for p in objects:
				if counter < start_position:
					counter += 1
					continue
				if counter >= end_position:
					break
				counter += 1
				if not p.isalias:
					send_message(source, tr('warp.point', x=round(p.x, 2), y=round(p.y, 2), z=round(p.z, 2), dimension=p.dimension, name=p.name, c=p.creator))
				else:
					send_message(source, tr('warp.pointalias', name=p.name, c=p.creator, to=p.alias))
			send_message(source, BIG_BLOCK_AFTER)

		@Literal(['set', 'add', 's'])
		def _set(self, source: MCDR.CommandSource, name: str, x: float, y: float, z: float, dimension: str):
			z = float(server.rcon_query('data get entity {} Pos[2]'.format(player)).split(": ")[-1][:-1])

			# if x is None:
			# 	if not source.is_player:
			# 		send_message(source, MCDR.RText(server.rtr('kpi.command.player_only'), color=MCDR.RColor.red))
			# 		return
			# 	x, y, z = get_player_pos(source.player)
			point = self.points.get_point(name)
			if len(name) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return
			
			if point is None:
				if self.points.points_count >= self.points.max_warp_points:
					send_message(source, MCDR.RText(tr('warp.points.full'), color=MCDR.RColor.red))
					return
				if isinstance(source, MCDR.PlayerCommandSource) and not self.has_force_permission(source):
					player_points_count = self.points.get_player_point_used(source.player)
					if player_points_count >= self.points.max_warp_points_per_player:
						send_message(source, MCDR.RText(tr('warp.points.full_per_player',
								count=player_points_count, limit=self.points.max_warp_points_per_player),
							color=MCDR.RColor.red))
						return
			elif not self._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.points.exists'), color=MCDR.RColor.red))
				return

			player = source.player
			gamemode = int(server.rcon_query('data get entity {} playerGameType'.format(player)).split(": ")[-1])

			if gamemode not in [0, 1, 2]:
				if source.get_permission_level() < 2:
					send_message(source, MCDR.RText(tr('warp.moderefused'), color=MCDR.RColor.red))
					return
			
			self.points.set_point(WarpPoint(x=x, y=y, z=z, dimension=dimension, name=name,
				creator=source.player if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=1))
			send_message(source, MCDR.RText(tr('warp.created', name) if point is None else tr('warp.updated', point.name), color=MCDR.RColor.green), log=True)

		@Literal('addhere')
		def sethere(self, source: MCDR.CommandSource, name: str):
			server = get_server_instance()
			#assert server.is_rcon_running()
			# if x is None:
			# 	if not source.is_player:
			# 		send_message(source, MCDR.RText(server.rtr('kpi.command.player_only'), color=MCDR.RColor.red))
			# 		return
			# 	x, y, z = get_player_pos(source.player)
			point = self.points.get_point(name)

			if len(name) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return

			if point is None:
				if self.points.points_count >= self.points.max_warp_points:
					send_message(source, MCDR.RText(tr('warp.points.full'), color=MCDR.RColor.red))
					return
				if isinstance(source, MCDR.PlayerCommandSource) and not self.has_force_permission(source):
					player_points_count = self.points.get_player_point_used(source.player)
					if player_points_count >= self.points.max_warp_points_per_player:
						send_message(source, MCDR.RText(tr('warp.points.full_per_player',
								count=player_points_count, limit=self.points.max_warp_points_per_player),
							color=MCDR.RColor.red))
						return
			elif not self._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.points.exists'), color=MCDR.RColor.red))
				return

			player = source.player

			x = float(server.rcon_query('data get entity {} Pos[0]'.format(player)).split(": ")[-1][:-1])
			y = float(server.rcon_query('data get entity {} Pos[1]'.format(player)).split(": ")[-1][:-1])
			z = float(server.rcon_query('data get entity {} Pos[2]'.format(player)).split(": ")[-1][:-1])

			dimension = eval(server.rcon_query('data get entity {} Dimension'.format(player)).split(": ")[-1])

			gamemode = int(server.rcon_query('data get entity {} playerGameType'.format(player)).split(": ")[-1])

			if gamemode not in [0, 1, 2]:
				if source.get_permission_level() < 2:
					send_message(source, MCDR.RText(tr('warp.moderefused'), color=MCDR.RColor.red))
					return

			self.points.set_point(WarpPoint(x=x, y=y, z=z, dimension=dimension, name=name,
				creator=source.player if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=1))
			send_message(source, MCDR.RText(tr('warp.created', name) if point is None else tr('warp.updated', point.name), color=MCDR.RColor.green), log=True)

		@Literal(['remove', 'r', 'rm'])
		def remove(self: Self, source: MCDR.CommandSource, name: str):
			point = self.points.get_point(name)
			if point is None: # or not source.has_permission(point.permission):
				send_message(source, MCDR.RText(tr('warp.points.not_exists', name), color=MCDR.RColor.red))
				return

			while point.isalias:
				_alias = point.alias
				point = self.points.get_point(_alias)
				if point is None: # or not source.has_permission(point.permission):
					send_message(source, MCDR.RText(tr('warp.points.not_exists', _alias), color=MCDR.RColor.red))
					return
					
			if source.get_permission_level() <= point.permission and source.player != point.creator:
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return
					
			self.points.remove_point(point.name)
			send_message(source, MCDR.RText(tr('warp.removed', point.name), color=MCDR.RColor.gold), log=True)

		@Literal(['rmalias'])
		def rmalias(self: Self, source: MCDR.CommandSource, name: str):
			point = self.points.get_point(name)
			if point is None: # or not source.has_permission(point.permission):
				send_message(source, MCDR.RText(tr('warp.points.not_exists', name), color=MCDR.RColor.red))
				return

			if not point.isalias:
				send_message(source, MCDR.RText(tr('warp.points.notalias', point.name), color=MCDR.RColor.red))
				return
							
			if source.get_permission_level() <= point.permission and source.player != point.creator:
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return
							
			self.points.remove_point(point.name)
			send_message(source, MCDR.RText(tr('warp.removed', point.name), color=MCDR.RColor.gold), log=True)
		
		@Literal(['rename', 're'])
		def rename(self: Self, source: MCDR.CommandSource, name: str, nname: str):
			point = self.points.get_point(name)

			if point is None: # or not source.has_permission(point.permission):
				send_message(source, MCDR.RText(tr('warp.points.not_exists', name), color=MCDR.RColor.red))
				return

			if source.get_permission_level() <= point.permission and source.player != point.creator:
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return

			if len(nname) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return
			
			# `warps.rename` is implemented as remove + create. Preserve a manual
			# category tag across that operation so the tag follows the renamed point.
			point_tags = self.rootset.categories.get_tags(point.name)
			old_name = point.name

			self.points.remove_point(old_name)
			self.points.set_point(WarpPoint(x=point.x, y=point.y, z=point.z, dimension=point.dimension, name=nname,
				creator=point.creator if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=1, isalias=point.isalias, alias=point.alias))

			# remove_point() automatically removes the old tags. Re-create all of them under
			# the new warp-point name so categories.json remains consistent.
			for point_tag in point_tags:
				self.rootset.categories.set_tag(nname, point_tag)
			send_message(source, MCDR.RText(tr('warp.renamed', o=name, n=nname), color=MCDR.RColor.gold), log=True)

		@Literal('disown')
		def disown(self: Self, source: MCDR.CommandSource, name: str):
			point = self.points.get_point(name)
			if point is None: # or not source.has_permission(point.permission):
				send_message(source, MCDR.RText(tr('warp.points.not_exists', name), color=MCDR.RColor.red))
				return

			while point.isalias:
				_alias = point.alias
				point = self.points.get_point(_alias)
				if point is None: # or not source.has_permission(point.permission):
					send_message(source, MCDR.RText(tr('warp.points.not_exists', _alias), color=MCDR.RColor.red))
					return
			
			if source.get_permission_level() <= point.permission and source.player != point.creator:
				send_message(source, MCDR.RText(tr('warp.permdenied'), color=MCDR.RColor.red))
				return
						
			point_tags = self.rootset.categories.get_tags(point.name)
			self.points.remove_point(point.name)
			self.points.set_point(WarpPoint(x=point.x, y=point.y, z=point.z, dimension=point.dimension, name=point.name,
				creator="**disowned" if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=2, isalias=point.isalias, alias=point.alias))
			for point_tag in point_tags:
				self.rootset.categories.set_tag(point.name, point_tag)
			send_message(source, MCDR.RText(tr('warp.disowned', o=name), color=MCDR.RColor.gold), log=True)

		@Literal(['alias'])
		def alias(self: Self, source: MCDR.CommandSource, name: str, nname: str):
			point = self.points.get_point(nname)
			if point is None: # or not source.has_permission(point.permission):
				send_message(source, MCDR.RText(tr('warp.points.not_exists', nname), color=MCDR.RColor.red))
				return

			while point.isalias:
				_alias = point.alias
				point = self.points.get_point(_alias)
				if point is None: # or not source.has_permission(point.permission):
					send_message(source, MCDR.RText(tr('warp.points.not_exists', _alias), color=MCDR.RColor.red))
					return
		
			if len(nname) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return
					
			self.points.set_point(WarpPoint(x=-1.0, y=-1.0, z=-1.0, dimension='alias', name=name,
				creator=source.player if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=1, isalias=True, alias=nname)) # 1
			send_message(source, MCDR.RText(tr('warp.alias', n=name, o=nname), color=MCDR.RColor.gold), log=True)

	def register_accept(self, source: MCDR.PlayerCommandSource, target: str,
		accept_call, reject_call=None,
		timeout_call=None, timeout: int | None = None) -> bool:
		assert_instanceof(source, MCDR.PlayerCommandSource)
		assert callable(accept_call)
		assert reject_call is None or callable(reject_call)
		assert timeout_call is None or callable(timeout_call)
		if target.lower() in self.__tpask_map:
			send_message(source, MSG_ID, MCDR.RText(tr('ask.player_req_exists', target), color=MCDR.RColor.red))
			return False
		name = source.player
		if name.lower() in self.__tpsender_map:
			send_message(source, MSG_ID, MCDR.RText(tr('ask.req_exists'), color=MCDR.RColor.red))
			return False

		def timeout_cb():
			self.__tpask_map.pop(target.lower())
			self.__tpsender_map.pop(name.lower())
			if timeout_call is not None:
				timeout_call()
		timer = None if timeout is None else new_timer(timeout, timeout_cb)

		def accept_cb(*args):
			if timer is not None:
				timer.cancel()
			self.__tpsender_map.pop(name.lower())
			dyn_call(accept_call, *args)

		def reject_cb(*args):
			if timer is not None:
				timer.cancel()
			self.__tpsender_map.pop(name.lower())
			if reject_call is not None:
				dyn_call(reject_call, *args)

		def cancel_cb(*args):
			if timer is not None:
				timer.cancel()
			self.__tpask_map.pop(target.lower())
			if reject_call is not None:
				dyn_call(reject_call, *args)

		self.__tpask_map[target.lower()] = (accept_cb, reject_cb)
		self.__tpsender_map[name.lower()] = cancel_cb
		return True
