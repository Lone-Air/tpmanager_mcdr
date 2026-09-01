 
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
		@call_with_root
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
				send_message(source, MCDR.RText(tr('warp.points.permdenied'), color=MCDR.RColor.red))
				return

			if len(nname) > 32:
				send_message(source, MCDR.RText(tr('warp.points.overlength'), color=MCDR.RColor.red))
				return
			
			self.points.remove_point(point.name)
			self.points.set_point(WarpPoint(x=point.x, y=point.y, z=point.z, dimension=point.dimension, name=nname,
				creator=point.creator if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=1, isalias=point.isalias, alias=point.alias))
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
				send_message(source, MCDR.RText(tr('warp.points.permdenied'), color=MCDR.RColor.red))
				return
						
			self.points.remove_point(point.name)
			self.points.set_point(WarpPoint(x=point.x, y=point.y, z=point.z, dimension=point.dimension, name=point.name,
				creator="**disowned" if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=2, isalias=point.isalias, alias=point.alias))
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
