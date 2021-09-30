import math

import Player
import Clan
import War
import CWLGroup
import CWLWar


cwl_clan_lineup_dict = {
    'clan': {},
    14: 0,
    13: 0,
    12: 0,
    11: 0,
    10: 0,
    9: 0,
    8: 0,
    7: 0,
    6: 0,
    5: 0,
    4: 0,
    3: 0,
    2: 0
}


# Player

def get_player(player_tag, header):
    return Player.get(player_tag, header)


def verify_token(api_key, player_tag, header):
    return Player.verify_token(api_key, player_tag, header)

# returns player.name and troop.lvl


def find_unit(player_obj, unit_name):
    unit_obj = player_obj.find_unit(unit_name)
    if unit_obj:
        # unit was found
        return unit_obj
    if not unit_obj:
        # unit was not found
        return None


def super_troop_unit_name(unit_name):
    for super_troop in Player.super_troop_list:
        if unit_name.lower() == super_troop.lower():
            return super_troop
    return None


# Clan
# todo DOCSTRING
def get_clan(clan_tag, header):
    return Clan.get(clan_tag, header)


# returns a string response of members that can donate the best of that unit
# todo put this into the clan framework
def donation(unit_name, clan, header):
    """
        Takes in the unit name and clan tag, returns a list of players
        who can donate.

        Returns an empty list if nobody can donate requested unit.
        Returns None if hero has been requested.

        Args:
            unit_name (str): Name of requested unit.
            clan (obj): Clan object.
            header (dict): Json header

        Returns:
            list: List of players who can donate.
    """

    class Donor(object):
        def __init__(self, player, unit):
            self.player = player
            self.unit = unit

    # get a member list to make less overall responses
    member_list = []
    for member in clan.members:
        player = Player.get(member.tag, header)

        # checking if they have the specified unit
        unit = player.find_unit(unit_name)
        if unit:
            member_list.append(Donor(player, unit))

    # if nobody has the requested unit
    if len(member_list) == 0:
        return member_list

    # if hero has been requested return None
    if member_list[0].player.find_hero(unit_name):
        return None

    donor_max = max(member.unit.lvl for member in member_list)

    # list of those that can donate
    donators = []

    # checking to see if anyone can donate max
    if (donor_max + clan.donation_upgrade) >= member_list[0].unit.max_lvl:
        # go thru each member and return the donors that can donate max
        for member in member_list:
            # if the member can donate max unit
            if (member.unit.lvl+clan.donation_upgrade) >= member.unit.max_lvl:
                # adding the donor's name to the donator list
                donators.append(member)
        return donators

    # since nobody can donate max
    # ! this still needs to be tested
    else:
        for member in member_list:
            troop = member.find_troop(unit_name)
            if troop.lvl >= donor_max:
                donators.append(member)
        return donators


def active_super_troop_search(unit_name, clan, header):
    """
        Takes in the unit name and clan object, returns a list of players
        who have super troop active.

        Returns an empty list if nobody has the super troop active.

        Args:
            unit_name (str): Name of requested unit.
            clan (obj): Clan object.
            header (dict): Json header

        Returns:
            list: List of players who can donate.
    """

    donor_list = []
    # getting a list of members with the given super_troop activated
    for member in clan.members:
        player = Player.get(member.tag, header)
        active_super_troops = player.find_active_super_troops()
        for super_troop in active_super_troops:
            # if the member has the requested active super troop add to list
            if super_troop.name == unit_name:
                donor_list.append(member)
                break
    return donor_list


# returns a string of the member's role
def response_member_role(player_name, clan_tag, header):
    clan = Clan.get(clan_tag, header)
    player_tag = clan.find_member(player_name)
    player = Player.get(player_tag, header)
    return player.role


# War
# todo DOCSTRING
def get_war(clan_tag, header):
    return War.get(clan_tag, header)


def war_no_attack_members(clan_tag, header):
    "returns a list of players that haven't attacked"
    war = War.get(clan_tag, header)

    if war.state == 'preparation':
        return []

    elif war.state == 'inWar':
        return war.no_attack()

    elif war.state == 'warEnded':
        return []

    else:
        return []


# todo update all for if not in CWL logic
# CWL Group

def get_cwl_group(clan_tag, header):
    return CWLGroup.get(clan_tag, header)


def cwl_lineup(cwl_group):
    if not cwl_group:
        return None
    clan_lineup = []
    for clan in cwl_group.clans:
        clan_lineup_dict = {
            'clan': {},
            14: 0,
            13: 0,
            12: 0,
            11: 0,
            10: 0,
            9: 0,
            8: 0,
            7: 0,
            6: 0,
            5: 0,
            4: 0,
            3: 0,
            2: 0
        }
        clan_lineup_dict['clan'] = clan
        for member in clan.members:
            clan_lineup_dict[member.th_lvl] += 1
        clan_lineup.append(clan_lineup_dict)
    return clan_lineup


# CWL War

# returns each member's CWL standing
def response_cwl_clan_standing(clan_tag, header):
    class ScoredMember(object):
        def __init__(self, tag, name, war_count, score):
            self.tag = tag
            self.name = name
            self.war_count = war_count
            self.score = score
    # get the CWLGroup object
    cwl_group = CWLGroup.get(clan_tag, header)

    if not cwl_group:
        return ['You are not in CWL.']

    # get a list of all CWLWar objects
    cwl_wars = []
    for i in range(0, len(cwl_group.rounds)):
        cwl_war = cwl_group.find_specified_war(clan_tag, i, header)
        cwl_wars.append(cwl_war)
    # get a list of all CWLWarMembers their scores
    cwl_war_members = []
    # find your clan
    for clan in cwl_group.clans:
        if clan.tag == clan_tag:
            # for each member in the CWLWarClan
            for member in clan.members:
                scored_member = ScoredMember(member.tag, member.name, 0, 0)
                # for each war getting that war score and war count
                for war in cwl_wars:
                    for war_member in war.clan.members:
                        if war_member.tag == member.tag:
                            scored_member.war_count += 1
                            scored_member.score += war_member.score
                            break
                if scored_member.war_count != 0:
                    avg_score = scored_member.score / scored_member.war_count
                    participation_multiplier = math.log(
                        scored_member.war_count, 7)
                    scored_member.score = avg_score * participation_multiplier
                cwl_war_members.append(scored_member)

    sorted_cwl_war_members = sorted(
        cwl_war_members, key=lambda member: member.score, reverse=True)
    return_string_list = []
    for member in sorted_cwl_war_members:
        return_string_list.append(
            f'{member.name} has a score of {round(member.score, 3)}')
    return return_string_list


# returns each specified member's CWL War score
def response_cwl_member_standing(player_obj, header):
    # find the player from the clan
    clan_obj = Clan.get(player_obj.clan_tag, header)

    # get the CWLGroup object
    cwl_group = CWLGroup.get(clan_obj.tag, header)

    if not cwl_group:
        return 'You are not in CWL'

    # get a list of all CWLWar objects
    cwl_wars = []
    for i in range(0, len(cwl_group.rounds)):
        cwl_war = cwl_group.find_specified_war(clan_obj.tag, i, header)
        cwl_wars.append(cwl_war)
    member_round_scores = []
    # find your clan
    found = False
    for clan in cwl_group.clans:
        if clan.tag == clan_obj.tag:
            cwl_group_clan = clan
            found = True
            break
    if not found:
        return 'Could not find your clan based on the clan tag provided'

    found = False
    for member in cwl_group_clan.members:
        if member.tag == player_obj.tag:
            found = True
            break
    if not found:
        return 'Could not find {player.name} in the CWL group.'

    for war in cwl_wars:
        for war_member in war.clan.members:
            if war_member.tag == player_obj.tag:
                member_round_scores.append(war_member.score)
                break

    if len(member_round_scores) == 0:
        return_string = f'{player_obj.name} did not participate in any wars.'

    elif len(member_round_scores) == 1:
        return_string = f'{player_obj.name} was in 1 war and had a score of {round(member_round_scores[0], 3)} for that war.'

    else:
        total_score = 0
        for round_score in member_round_scores:
            total_score += round_score
        avg_score = total_score / len(member_round_scores)
        participation_multiplier = math.log(len(member_round_scores), 7)
        member_score = avg_score * participation_multiplier

        return_string = f"{player_obj.name} was in {len(member_round_scores)} wars with an overall score of {round(member_score, 3)}. {player_obj.name}'s scores are: "
        for cwl_round_score in member_round_scores:
            return_string += f'{round(cwl_round_score, 3)}, '
        # removes the last 2 characters ', ' of the string
        return_string = return_string[:-2]
        return_string += '.'

    return return_string
