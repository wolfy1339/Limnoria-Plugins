###
# Copyright (c) 2011, Anthony Boot
# Copyright (c) 2015-2016, wolfy1339
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS'
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import supybot.ircmsgs as ircmsgs
import supybot.ircdb as ircdb
import random
import json


class Rpg(callbacks.Plugin):
    """
    A text based RPG for IRC channels. Requires the user to be registered
    with supybot to use it. Command list:
    move stats run new loc viewarea
    """
    threaded = True

    class rpg(callbacks.Commands):
        def __init__(self):
            self.gameChannel = "#BMN"
            self.playerData = {}
            self.mapData = {}
            self.mapInfo = {}
            self.monsterData = {}
            self.itemData = {}
            self.consolechannel = "##wolfy-console"
            self.filepath = "/home/wolfy1339/BMNBot-New/plugins/Rpg/"

        # Game Commands
        def reloadData(self, irc, msg, args):
            if not ircdb.users.getUser(msg.prefix)._checkCapability("admin"):
                irc.error("Only people with \"Admin\" can do that.")
                return
            else:
                self._getPlayerData()
                self._getMapData()
                self._getMapInfo()
                with open(self.filepath + "monsters.json") as f:
                    self.monsterData = json.load(f)
                    self._getItemsFile()
                    irc.replySuccess()
        reloaddata = wrap(reloadData)

        def genMap(self, irc, msg, args, width, height):
            if not ircdb.users.getUser(msg.prefix)._checkCapability("owner"):
                irc.error("Only people with \"Admin\" can do that.")
                return
            else:
                if not width or not height:
                    width = height = 52
                else:
                    try:
                        width = int(width)
                        height = int(height)
                    except:
                        irc.error("Invalid arguments given.")
                        return

            random.seed()
            seed = random.random()
            random.seed(seed)
            terrain = []
            terrain += "#####:~..............................................."
            #          # is wall  : is boss  ~ is item  . is nothing.
            rand = {}
            terrainmap = ""

            self._sendDbg(irc, "Generating new usermap..")

            x = -1
            while x < width:
                terrainline = ""
                x += 1
                y = -1
                while y < height:
                    y += 1
                    if x is 0 or x is width or y is 0 or y is height:
                        terrainline += terrain[0]
                        continue
                    if x is int(width / 2) and y is int(height / 2):
                        terrainline += "@"
                        y += 1
                    rand[1] = int(random.random() * (len(terrain) - 1))
                    rand[2] = int(random.random() * (len(terrain) - 1))
                    rand[3] = int(random.random() * (len(terrain) - 1))
                    rand[4] = int(random.random() * (len(terrain) - 1))
                    if rand[1] is rand[2] and rand[1] is rand[3]:
                        terrainline += terrain[rand[1]]
                    elif rand[1] is rand[2] or rand[1] is rand[3]:
                        terrainline += terrain[rand[1]]
                    elif rand[2] is rand[3]:
                        terrainline += terrain[rand[2]]
                    else:
                        terrainline += terrain[rand[4]]
                terrainmap += terrainline + "\n"

                data = {
                    "width": width,
                    "height": height,
                    "homeY": (height / 2),
                    "homeX": int(width / 2),
                    "homeLoc": int((height / 2) + ((width / 2) * (width + 2))),
                    "desc": "Random Generation."
                }

                with open(self.filepath + "mapData.json", "w") as f:
                    json.dump(data, f)
                self._saveMapData(terrainmap)
                irc.replySuccess("Map regeneration")
                self._sendDbg(
                    irc, ("Map created and saved to map.txt,"
                          " info saved to mapData.txt"))

                playerData = self.playerData
                for player in playerData:
                    playerData[player]["Loc"] = (
                        height / 2) + ((width / 2) * (width + 2))
                self._savePlayerData(playerData)
                self._sendDbg(irc, "Players relocated successfully.")
                irc.replySuccess("Players Relocated to Home")

#            if (self.serverUrl)
# submit  =  utils.web.getUrl(self.serverUrl+"?m = %s&w = %i&h = %&hm =
# %i&hy = %i

        genmap = wrap(genMap,
                      [optional("somethingWithoutSpaces"),
                       optional("somethingWithoutSpaces")])

        def stats(self, irc, msg, args):
            player = self._checkPlayer(irc, msg)
            playerData = self.playerData[player]

            level = playerData["Lvl"]
            exp = playerData["Exp"]
            next = self._getNextLevelXp(player)
            baseAtk = playerData["Atk"]
            totalAtk = baseAtk + playerData["Item"]["rArm"]["Power"]
            baseDef = playerData["Def"]
            totalDef = baseDef + \
                playerData["Item"]["Head"]["Power"] + \
                playerData["Item"]["Torso"]["Power"]
            luck = playerData["Luc"]
            block = playerData["Item"]["lArm"]["Power"]
            deaths = playerData["Deaths"]
            hp = playerData["HP"]
            mhp = playerData["MHP"]

            weapon = playerData["Item"]["rArm"]["Name"]
            helmet = playerData["Item"]["Head"]["Name"]
            shield = playerData["Item"]["lArm"]["Name"]
            armour = playerData["Item"]["Torso"]["Name"]

            irc.reply(("{0} is at Level {1} with {2} experience; {3} is"
                       " needed for the next level. You have {4}/{5} HP. "
                       "Your base attack is {6} and is boosted to {7} by your "
                       "{8} Sword. Your base defence is {9},  boosted to {10} "
                       "with your {11} Helmet and {12} Armour."
                       "Your {13} Shield gives you a {14}% chance to block "
                       "attacks. Your Luck rating is {15}. "
                       "You have died {16} times."
                       ).format(player, level, exp, next, hp, mhp, baseAtk, totalAtk, weapon, baseDef, totalDef, helmet, armour, shield, block, luck, deaths))
        stats = wrap(stats)

        def new(self, irc, msg, args):
            player = self._checkPlayer(irc, msg, 1)
            playerData = self.playerData

            playerData[player] = {}
            playerData[player]["Lvl"] = 1
            playerData[player]["Exp"] = 0
            playerData[player]["MHP"] = int(random.random() * 20) + 15
            playerData[player]["HP"] = playerData[player]["MHP"]
            playerData[player]["Atk"] = int(random.random() * 5) + 1
            playerData[player]["Def"] = int(random.random() * 5) + 1
            playerData[player]["Spd"] = int(random.random() * 5) + 1
            playerData[player]["Luc"] = int(random.random() * 2) + 1
            playerData[player]["Item"] = {}
            playerData[player]["Item"]["Head"] = {
                "Name": "Cloth",
                "Power": int(random.random() * 3)
            }
            playerData[player]["Item"]["Torso"] = {
                "Name": "Cloth", "Power": int(random.random() * 3)}
            playerData[player]["Item"]["lArm"] = {
                "Name": "Wooden",
                "Power": int(random.random() * 5)
            }
            playerData[player]["Item"]["rArm"] = {
                "Name": "Wooden",
                "Power": int(random.random() * 3)
            }
            playerData[player]["Deaths"] = 0
            playerData[player]["Loc"] = self.mapInfo["homeLoc"]
            playerData[player]["force"] = False

            self._sendDbg(irc, player + " has been reset/created")
            self._savePlayerData(playerData)
            self.rpgStats(irc, msg, args)
        new = wrap(new)

        def location(self, irc, msg, args):
            player = self._checkPlayer(irc, msg)
            location = self.playerData[player]["Loc"]
            mapInfo = self.mapInfo

            x = 0
            while True:
                if location > mapInfo["width"]:
                    location -= (mapInfo["width"] + 2)
                    x += 1
                else:
                    break
            y = location
            homeX = self.mapInfo["homeX"]
            homeY = self.mapInfo["homeY"]
            irc.reply((
                "You are located at ({0}, {1})."
                " Home is at ({2}, {3})").format(x, y, homeX, homeY))
        loc = wrap(location)

        def ViewArea(self, irc, msg, args):
            player = self._checkPlayer(irc, msg)
            location = self.playerData[player]["Loc"]
            mapData = self.mapData
            mapInfo = self.mapInfo

            area = []
            area += mapData[location - (mapInfo["width"] + 3)]
            area += mapData[location - (mapInfo["width"] + 2)]
            area += mapData[location - (mapInfo["width"] + 1)]
            area += mapData[location - 1]
            area += mapData[location + 1]
            area += mapData[location + (mapInfo["width"] + 1)]
            area += mapData[location + (mapInfo["width"] + 2)]
            area += mapData[location + (mapInfo["width"] + 3)]

            for x in area:
                line = area.index(x)
                if x is ".":
                    area[line] = "Nothing"
                elif x is "#":
                    area[line] = "Wall"
                elif x is "~":
                    area[line] = "Item"
                elif x is ":":
                    area[line] = "Boss"
                elif x is "@":
                    area[line] = "Home"

            irc.reply(("NW: {0} - N: {1} - NE: {2} - W: {3} - E: {4} - SW: {5}"
                       "- S: {6} - SE: {7}").format(
                           area[0],
                           area[1],
                           area[2],
                           area[3],
                           area[4],
                           area[5],
                           area[6],
                           area[7])
                      )
        viewArea = wrap(viewArea)

        def forceBattle(self, irc, msg, args):
            player = self._checkPlayer(irc, msg)
            if self.playerData[player]["force"]:
                self.playerData[player]["force"] = False
                text = "will no longer enter a battle on the next turn."
                irc.reply("{0} {1}".format(player.capitalize(), text),
                          prefixNick=False)
            else:
                self.playerData[player]["force"] = True
                text = "will enter a monster battle on their next turn."
                irc.reply("{0} {1}".format(player.capitalize(), text),
                          prefixNick=False)
        forceBattle = wrap(forceBattle)

        def move(self, irc, msg, args, direction, number):
            player = self._checkPlayer(irc, msg)
            playerData = self.playerData
            mapData = self.mapData
            mapInfo = self.mapInfo
            direction = direction.upper()

            try:
                number = int(number)
            except:
                number = 1
            if number == 0:
                number = 1

            x = 0
            while x < number:
                if direction == "NW":
                    if mapData[playerData[player]["Loc"] -
                               (mapInfo["width"] + 3)] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] -= (mapInfo["width"] + 3)
                        self._savePlayerData(playerData)
                elif direction == "N":
                    if mapData[playerData[player]["Loc"] -
                               (mapInfo["width"] + 2)] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] -= (mapInfo["width"] + 2)
                        self._savePlayerData(playerData)
                elif direction == "NE":
                    if mapData[playerData[player]["Loc"] -
                               (mapInfo["width"] + 1)] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] -= (mapInfo["width"] + 1)
                        self._savePlayerData(playerData)
                elif direction == "W":
                    if mapData[playerData[player]["Loc"] - 1] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] -= 1
                        self._savePlayerData(playerData)
                elif direction == "E":
                    if mapData[playerData[player]["Loc"] + 1] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] += 1
                        self._savePlayerData(playerData)
                elif direction == "SW":
                    if mapData[playerData[player]["Loc"] +
                               (mapInfo["width"] + 1)] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] += (mapInfo["width"] + 1)
                        self._savePlayerData(playerData)
                elif direction == "S":
                    if mapData[playerData[player]["Loc"] +
                               (mapInfo["width"] + 2)] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] += (mapInfo["width"] + 2)
                        self._savePlayerData(playerData)
                elif direction == "SE":
                    if mapData[playerData[player]["Loc"] +
                               (mapInfo["width"] + 3)] is "#":
                        irc.error("You can't move there.")
                        return
                    else:
                        playerData[player]["Loc"] += (mapInfo["width"] + 3)
                        self._savePlayerData(playerData)
                else:
                    irc.error(
                        "Move failed. you gave {0} as a direction. {1}".format(direction, str(type(direction))))

                if mapData[playerData[player]["Loc"]] is "~":
                    self._genItem(player, 2)
    #             mapData[playerData[player]["Loc"]] = "."
                    self._saveMapData()

                elif mapData[playerData[player]["Loc"]] is ":":
                    self._doBattle(irc, player, 2, msg.nick)

                elif mapData[playerData[player]["Loc"]] is ".":
                    if playerData[player]["force"] is True:
                        self._sendDbg(irc, "Battle Forced")
                        playerData[player]["force"] = False
                        self._doBattle(irc, player, 1, msg.nick)
                        self._savePlayerData(playerData)
                    elif int(random.random() * 100) < 5:
                        self._doBattle(irc, player, 1, msg.nick)

                elif mapData[playerData[player]["Loc"]] is "@":
                    playerData[player]["HP"] = playerData[player]["MHP"]
                    text = "Your health has been restored."
#                   irc.reply(text)
                    self._notice(irc, msg.nick, text)
                    self._savePlayerData(playerData)
                x += 1

        move = wrap(move, ["somethingWithoutSpaces", optional("int")])

    #  Engine functions
        gameChan = self.gameChannel

        def _checkPlayer(self, irc, msg, new=0):
            if (msg.args[0] != self.gameChannel):
                if msg.nick in irc.state.channels[gameChan].users:
                    irc.error((
                        "That command cannot be sent in this channel. "
                        "Please try again in {0}").format(gameChan))
                else:
                    irc.error(
                        "You need to join {0} and use that command there.".format(gameChan))
                    irc.queueMsg(ircmsgs.invite(msg.nick, gameChan))
                return None

            try:
                player = str(ircdb.users.getUser(msg.prefix))
                player = player.split("name = \"")[1].split("\", ")[0]
            except KeyError:
                irc.errorNotRegistered()

            try:
                test = self.playerData[player]
            except:
                if new is 0:
                    irc.error("Use rpg new to create an RPG character first.")
            return player

        def _getPlayerData(self):
            with open(self.filepath + "players.json", "r") as f:
                self.playerData = json.load(f)

        def _savePlayerData(self, data):
            with open(self.filepath + "players.json", "w") as f:
                json.dump(data, f)
            self._getPlayerData()

        def _getMapData(self):
            with open(self.filepath + "map.txt", "r") as f:
                self.mapData = f.read()
            self._getMapInfo()

        def _saveMapData(self, data):
            with open(self.filepath + "map.txt", "w") as f:
                f.write(data)
            self._getMapData()

        def _getMapInfo(self):
            with open(self.filepath + "mapData.json", "r") as f:
                self.mapInfo = json.load(f)

        def _getItemsFile(self):
            with open(self.filepath + "items.json", "r") as f:
                self.itemData = json.load(f)

        def _sendDbg(self, irc, data):
            data = "RPG: " + str(data)
            if(self.consolechannel):
                irc.queueMsg(ircmsgs.privmsg(self.consolechannel, data))
            self.log.debug(data)

        def _doBattle(self, irc, player, level=1, nick="StewieGriffin"):
            random.seed()
            playerData = self.playerData
            if level is 1:
                monster = self._genMonster(player)
            if level is 2:
                monster = self._genBoss(player)

            irc.reply("{0} has encountered Level {1} {2} and could potentially earn {3} experience!".format(
                    player, monster["Lvl"], monster["Name"], monster["Exp"]), prefixNick=False)

            self._sendDbg(irc, monster)
            battleData = {
                "player": {
                    "atks": 0,
                    "blocks": 0,
                    "crits": 0
                },
                "monster": {
                    "atks": 0,
                    "crits": 0,
                    "evades": 0
                },
                "rounds": 0
            }

            def _doMonster():
                if (random.random() * 100 <
                        playerData["Item"]["rArm"]["Power"]):
                    battleData["player"]["blocks"] += 1
                else:
                    battleData["monster"]["atks"] += 1
                    atkValue = int(random.random() * (monster["Atk"])) + 2
                    if (random.random() * 100 < 2):
                        atkValue *= 2
                        battleData["monster"]["crits"] += 1
                    playerData[player]["HP"] -= (atkValue -
                                                 (playerData["Def"] *
                                                  playerData["Item"]["Torso"]["Power"]))
                    if playerData[player]["HP"] <= 0:
                        return monster["Name"]

            def _doPlayer():
                if random.random() * 100 < 10:
                    battleData["monster"]["evades"] += 1
                else:
                    battleData["player"]["atks"] += 1
                    playerAtk = int(random.random(
                    ) * (playerData[player]["Atk"] + playerData["Item"]["lArm"]["Power"])) + 2
                    if(random.random() * 100 < playerData["Luc"]):
                        playerAtk *= 2
                        battleData["player"]["crits"] += 1
                    monster["HP"] -= playerAtk
                    if monster["HP"] <= 0:
                        return player

            winner = None
            while winner is None:
                battleData["rounds"] += 1
                if monster["Spd"] > playerData["Spd"]:
                    winner = _doMonster()
                    if winner is None:
                        winner = _doPlayer()
                else:
                    winner = _doPlayer()
                    if winner is None:
                        winner = _doMonster()

            if winner is player:
                self._playerWin(irc, player, monster, playerData)
            else:
                self._playerDead(irc, player, monster, playerData)

            bDataString = "Battle lasted {0} rounds,  you scored {1} hits, ".format(
                     battleData["rounds"], battleData["player"]["atks"])
            bDataString += "{0} were critical and {1} were evaded attacks. ".format(
                     battleData["player"]["crits"], battleData["monster"]["evades"])
            bDataString += "{0} made {1} attacks,  {2} were critical and {3}".format(
                     monster["Name"], battleData["monster"]["atks"], battleData["monster"]["crits"], battleData["player"]["blocks"])
            bDataString += " were blocked."
            self._notice(irc, nick, bDataString)
#           irc.reply(bDataString, prefixNick=False)

        def _playerDead(self, irc, player, monster, playerData):
            text = "OOOOOOH YOU JUST GOT PWNT! - "
            text += "You\"ve been sent back home and fully healed. "
            text += "Luckily theres no penalties for dying."
            # irc.reply(text)
            self._notice(irc, msg.nick, text)
            playerData[player]["HP"] = playerData[player]["MHP"]
            playerData[player]["Loc"] = self.mapInfo["homeLoc"]
            playerData[player]["Deaths"] += 1
            self._savePlayerData(playerData)

        def _playerWin(self, irc, player, monster, playerData):
            winString = "{0} won the battle! {1} gained {2} experience.".format(
                player, player, monster["Exp"])
            self._checkLevelUp(irc, player, monster["Exp"])
            if(int(random.random() * 100) < 5):
                itemWon = self._genItem(player)
                winString = " You found a {0} {1},  ".format(
                    itemWon["name"], itemWon["item"].capitalize())
                better = False
                oldEquip = {}
                if itemWon["item"] is "sword":
                    if itemWon["Power"] > playerData[
                            player]["Item"]["lArm"]["Power"]:
                        oldEquip["Name"] = playerData[player]["lArm"]["Name"]
                        oldEquip["Power"] = playerData[player]["lArm"]["Power"]
                        playerData[player]["lArm"]["Power"] = itemWon["power"]
                        playerData[player]["lArm"]["Name"] = itemWon["name"]
                        better = True
                elif itemWon["item"] is "shield":
                    if itemWon["Power"] > playerData[
                            player]["Item"]["rArm"]["Power"]:
                        oldEquip["Name"] = playerData[player]["rArm"]["Name"]
                        oldEquip["Power"] = playerData[player]["rArm"]["Power"]
                        playerData[player]["rArm"]["Power"] = itemWon["power"]
                        playerData[player]["rArm"]["Name"] = itemWon["name"]
                        better = True
                elif itemWon["item"] is "helmet":
                    if itemWon["Power"] > playerData[
                            player]["Item"]["Head"]["Power"]:
                        oldEquip["Name"] = playerData[player]["Head"]["Name"]
                        oldEquip["Power"] = playerData[player]["Head"]["Power"]
                        playerData[player]["Head"]["Power"] = itemWon["power"]
                        playerData[player]["Head"]["Name"] = itemWon["name"]
                        better = True
                elif itemWon["item"] is "armour":
                    if itemWon["Power"] > playerData[
                            player]["Item"]["Torso"]["Power"]:
                        oldEquip["Name"] = playerData[player]["Torso"]["Name"]
                        oldEquip["Power"] = playerData[
                            player]["Torso"]["Power"]
                        playerData[player]["Torso"]["Power"] = itemWon["power"]
                        playerData[player]["Torso"]["Name"] = itemWon["name"]
                        better = True

                if better:
                    winString += " its better than your old {0} {1},  so you discard it and equip the {2} {3}".format(
                            oldEquip["Name"], itemWon["item"].capitalize(), itemWon["name"], itemWon["item"].capitalize())
                else:
                    winString += " unfortunlatly your old {0} {1} is better,  so you throw the {2} {3} aside".format(
                            oldEquip["Name"], itemWon["item"].capitalize(), itemWon["name"], itemWon["item"].capitalize())
                self._savePlayerData(playerData)
            irc.reply(winString, prefixNick=False)

        def _genItem(self, player, level=1):
            playerData = self.playerData
            itemData = self.itemData
            genChance = (100 - playerData[player]["Luc"]) / (level + 1)
            itemType = int(random.random() * 3)
            itemToReturn = possibleItem = {}

            if itemType is 0:  # Sword
                possibleItem["item"] = "sword"

                itemBase = False
                while itemBase is False:
                    possibleItem = itemData["swords"][
                        int(random.random() * len(itemData["swords"]))]
                    if int(random.random() * genChance) < possibleItem[3]:
                        itemBase = possibleItem
                        itemToReturn["name"] = possibleItem[0]
                        itemToReturn["power"] = int(
                            (random.random() * (possibleItem[2] - possibleItem[1])) + possibleItem[1])
            else:
                if itemType is 1:  # Shield
                    possibleItem["item"] = "shield"
                elif itemType is 2:  # Helmet
                    possibleItem["item"] = "helmet"
                elif itemType is 3:  # Torso
                    possibleItem["item"] = "armour"

                itemBase = False
                while itemBase is False:
                    possibleItem = itemData["defence"][
                        int(random.random() * len(itemData["defence"]))]
                    if int(random.random() * genChance < possibleItem[3]):
                        itemBase = possibleItem
                        itemToReturn["name"] = possibleItem[0]
                        itemToReturn["power"] = int(
                            (random.random() * (possibleItem[2] - possibleItem[1])) + possibleItem[1])

            itemBoost = False
            while itemBoost is False:
                booster = itemData["modifiers"][
                    random.randint(0, len(itemData["modifiers"]) - 1)]
                print(booster)
                if genChance < booster:
                    itemBoost = booster
                    itemToReturn["name"] = "{0} {1}".format(
                        booster[0], itemToReturn["name"])
                    itemToReturn["power"] = itemToReturn[
                        "power"] * (random.random() * (booster[2] - booster[1])) + booster[1]

            return itemToReturn

        def _genMonster(self, player):
            monster = {}
            monster["Lvl"] = self.playerData[player][
                "Lvl"] + (int(random.random() * 5))
            monster["Atk"] = int(
                (random.random() * (7 * monster["Lvl"])) + 1) + 10
            monster["Def"] = int(
                (random.random() * (7 * monster["Lvl"])) + 1) + 10
            monster["MHP"] = int(
                (random.random() * (7 * monster["Lvl"])) + 1) + 15
            monster["HP"] = monster["MHP"]
            monster["Name"] = self.monsterData["monsters"][
                int(random.random() * len(self.monsterData["monsters"]))]
            monster["Spd"] = int((random.random() * (5 * monster["Lvl"])) + 1)
            monster["Exp"] = int(
                (random.random() * monster["Lvl"]) + (self.playerData[player]["Lvl"] / 2)) + 1
            return monster

        def _genBoss(self, player):
            monster = {}
            pLvl = self.playerData[player]["Lvl"]
            boss = self.monsterData["boss"]
            monsers = self.monsterData["monsters"]
            monster["Lvl"] = pLvl + (int(random.random() * 5))
            mLvl = monster["Lvl"]
            monster["Atk"] = int(
                (random.random() * (14 * mLvl)) + 1) + 10
            monster["Def"] = int(
                (random.random() * (14 * mLvl)) + 1) + 10
            monster["MHP"] = int(
                (random.random() * (14 * mLvl)) + 1) + 15
            monster["HP"] = monster["MHP"]
            monster["Name"] = boss["names"][int(random.random() * len(boss[
                                                                    "names"]))] + "\"s " + monsters[int(random.random() * len(monsters))]
            monster["Spd"] = int((random.random() * (7 * mLvl)) + 1)
            monster["Exp"] = int(
                (random.random() * mLvl) + (pLvl / 2) + 1) + 5
            monster["pen"] = boss["pen"][
                int(random.random() * len(boss["pen"]))]
            return monster

        def _checkLevelUp(self, irc, player, xp):
            data = self.playerData
            playerData = data[player]
            nLvl = self._getNextLevelXp(player)
            playerData[player]["Exp"] += xp
            if playerData["Exp"] >= nLvl:
                playerData["MHP"] += int(random.random() * 7)
                playerData["Atk"] += int(random.random() * 7)
                playerData["Def"] += int(random.random() * 7)
                playerData["Spd"] += int(random.random() * 7)
                playerData["Luc"] += int(random.random() * 4)
                playerData["Lvl"] += 1
                irc.reply((
                    "{0} has leveled up,  they are now level {1}. "
                    "New stats are Attack: {2}, Defence: {3},"
                    " Speed: {4} and Luck: {5}").format(
                        player,
                        playerData["Lvl"],
                        playerData["Atk"],
                        playerData["Def"],
                        playerData["Spd"],
                        playerData["Luc"]),
                    prefixNick=False)
            self._savePlayerData(data)

        def _getNextLevelXp(self, player):
            levelBaseXp = 50
            pLvl = self.playerData[player]["Lvl"]
            return (levelBaseXp * pLvl) + ((levelBaseXp * pLvl) / 2)

        def _notice(self, irc, user, text):
            irc.queueMsg(ircmsgs.IrcMsg("NOTICE {0} :{1}".format(user, text)))
Class = Rpg

# vim:set shiftwidth = 4 softtabstop = 4 expandtab textwidth = 79:
