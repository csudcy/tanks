import os

import cherrypy

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import mount as mount_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template = 'index.html')
    def index(self):
        # Get the list of teams for the current user
        team_infos = db.Session.query(
            db.Team.uuid,
            db.Team.name,
            db.Team.game,
        ).filter(
            db.Team.creator == cherrypy.request.user
        ).order_by(
            db.Team.name,
        ).all()

        # Process them into a usable format
        teams = []
        for team_info in team_infos:
            teams.append({
                'uuid': team_info[0],
                'name': team_info[1],
                'game': games.GAME_DICT[team_info[2]].name,
            })


        # Now get matches for the current user
        """
        match_infos = db.Session.query(
            db.Match.uuid,
            db.Match.team_file_1.team.name,
            db.Match.team_file_2.team.name,
            db.Match.game,
        ).filter(
            db.Match.creator == cherrypy.request.user,
            db.Match.tournament == None,
        ).all()
        """

        team_1 = db.sa_orm.aliased(db.Team)
        team_2 = db.sa_orm.aliased(db.Team)
        team_file_1 = db.sa_orm.aliased(db.TeamFile)
        team_file_2 = db.sa_orm.aliased(db.TeamFile)
        match_infos = db.Session.query(
            db.Match.uuid,
            team_1.name,
            team_2.name,
            db.Match.game,
        ).join(
            team_file_1,
            db.Match.team_file_1
        ).join(
            team_file_2,
            db.Match.team_file_2
        ).join(
            team_1,
            team_file_1.team
        ).join(
            team_2,
            team_file_2.team
        ).filter(
            db.Match.creator == cherrypy.request.user,
            db.Match.tournament == None,
        ).all()

        # Process them into a usable format
        matches = []
        for match_info in match_infos:
            matches.append({
                'uuid': match_info[0],
                'team_1': match_info[1],
                'team_2': match_info[2],
                'game': games.GAME_DICT[match_info[3]].name,
            })
        #matches.reverse()


        # Now get tournaments for the current user
        tournament_infos = db.Session.query(
            db.Tournament.uuid,
            db.Tournament.game,
        ).filter(
            db.Tournament.creator == cherrypy.request.user,
        )

        # Process them into a usable format
        tournaments = []
        for tournament_info in tournament_infos:
            tournaments.append({
                'uuid': tournament_info[0],
                'game': games.GAME_DICT[tournament_info[1]].name,
            })

        return {
            'games': games.GAME_LIST,
            'teams': teams,
            'matches': matches,
            'tournaments': tournaments
        }


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
