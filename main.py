import math
import webbrowser
from espn_api.football import League

WEEK_NUM = 1
ESPN_PROCESSED = False

def WriteMatchupScores(file, boxScores):
    file.write("**Match Summaries for week " + str(WEEK_NUM) + "**\n")
    file.write("----------------------------------------------------------\n")

    for boxScore in boxScores:
        if (boxScore.home_team == 0 or boxScore.away_team == 0):
            continue

        homeName = boxScore.home_team.team_name + "(" + str(boxScore.home_team.wins) + "-" + str(boxScore.home_team.losses) + ")"
        awayName = boxScore.away_team.team_name + "(" + str(boxScore.away_team.wins) + "-" + str(boxScore.away_team.losses) + ")"
        if (boxScore.home_score > boxScore.away_score):
            file.write("**" + homeName + "** vs. " + awayName + "\n")
        else:
            file.write(homeName + " vs. **" + awayName + "**\n")

        file.write(boxScore.home_team.team_name + " score: " + str(boxScore.home_score) + "\n")
        file.write(boxScore.away_team.team_name + " score: " + str(boxScore.away_score) + "\n")
        file.write("----------------------------------------------------------\n\n")

    file.write("\n")

def GetTopScorers(file, league):
    file.write("**TOP SCORERS**\n")

    topScorers = league.top_scorer()
    
    for i in range(3):
        file.write(topScorers[i].team_name + ": " + str(round(topScorers[i].points_for, 2)) + "\n")
    file.write("\n\n")

def GetBottomScorers(file, league):
    file.write("**BOTTOM SCORERS**\n")

    bottomScorers = league.least_scorer()
    
    for i in range(3):
        file.write(bottomScorers[i].team_name + ": " + str(round(bottomScorers[i].points_for, 2)) + "\n")
    file.write("\n\n")

def GetBestBench(file, boxScores):
    file.write("** THE PRESTEGIOUS BEST BENCH AWARD **\n")
    teamName = ""
    benchScore = 0

    for matchup in boxScores:
        tempScore = 0
        if (matchup.home_team != 0):
            for player in matchup.home_lineup:
                if (player.slot_position == "BE"):
                    tempScore += player.points
            if tempScore > benchScore:
                teamName = matchup.home_team.team_name
                benchScore = tempScore
        tempScore = 0
        if matchup.away_team != 0:
            for player in matchup.away_lineup:
                if (player.slot_position == "BE"):
                    tempScore += player.points
            if tempScore > benchScore:
                teamName = matchup.away_team.team_name
                benchScore = tempScore
    file.write(teamName + ": " + str(round(benchScore, 2)) + "\n\n\n")

def GetWorstBench(file, boxScores):
    file.write("** THE PITIFUL WORST BENCH AWARD **\n")
    teamName = ""
    benchScore = 9999999

    for matchup in boxScores:
        tempScore = 999999
        if matchup.home_team != 0:
            for player in matchup.home_lineup:
                if (player.slot_position == "BE"):
                    tempScore += player.points
            if tempScore < benchScore:
                teamName = matchup.home_team.team_name
                benchScore = tempScore
        tempScore = 0
        if matchup.away_team != 0:
            for player in matchup.away_lineup:
                if (player.slot_position == "BE"):
                    tempScore += player.points
            if tempScore < benchScore:
                teamName = matchup.away_team.team_name
                benchScore = tempScore
    file.write(teamName + ": " + str(round(benchScore, 2)) + "\n\n\n")

def GetUpsets(file, boxScores):
    file.write("**UPSETS OF THE WEEK**\n")

    for matchup in boxScores:
        if (matchup.home_team == 0 or matchup.away_team == 0):
            continue

        homeProj = 0;
        awayProj = 0;
        for player in matchup.away_lineup:
            if (player.slot_position != "BE" and player.slot_position != "IR"):
                awayProj += player.projected_points
        for player in matchup.home_lineup:
            if (player.slot_position != "BE" and player.slot_position != "IR"):
                homeProj += player.projected_points

        if (homeProj > awayProj and matchup.home_score < matchup.away_score):
            file.write(matchup.home_team.team_name + " was projected to beat " + matchup.away_team.team_name + " by " + 
                       str(round(homeProj-awayProj, 2)) + " points, but lost by " + str(round(matchup.away_score - matchup.home_score, 2)) + " points\n");
        elif (homeProj < awayProj and matchup.home_score > matchup.away_score):
            file.write(matchup.away_team.team_name + " was projected to beat " + matchup.home_team.team_name + " by " + 
                       str(round(awayProj-homeProj, 2)) + " points, but lost by " + str(round(matchup.home_score - matchup.away_score, 2)) + " points\n");
    file.write("\n\n")

def CouldHaveWonIf(file, boxScores):
    file.write("** COULD HAVE WON IF... **\n")
    for matchup in boxScores:
        if (matchup.home_team == 0 or matchup.away_team == 0):
            continue
        homeLoss = matchup.home_score < matchup.away_score
        if (homeLoss):
            OptimalScoreAndTeam = GetOptimalScore(matchup.home_lineup)
            if (OptimalScoreAndTeam[0] > matchup.away_score):
                file.write(matchup.home_team.team_name + " could have won by " + str(round(OptimalScoreAndTeam[0] - matchup.away_score, 2)) +
                           " if they had started:\n")
                for player in OptimalScoreAndTeam[1]:
                    file.write(player + "\n")
                file.write("\n")
        else:
            OptimalScoreAndTeam = GetOptimalScore(matchup.away_lineup)
            if (OptimalScoreAndTeam[0] > matchup.home_score):
                file.write(matchup.away_team.team_name + " could have won by " + str(round(OptimalScoreAndTeam[0] - matchup.home_score, 2)) +
                           " if they had started:\n")
                for player in OptimalScoreAndTeam[1]:
                    file.write(player + "\n")
                file.write("\n")

def GetBiggestBlowout(file, boxScores):
    file.write("** THE BIGGEST BLOWOUT **\n")
    biggestBlowoutMatch = boxScores[0]
    blowoutMargin = -1
    for matchup in boxScores:
        if (matchup.home_team == 0 or matchup.away_team == 0):
            continue
        if abs(matchup.home_score - matchup.away_score) > blowoutMargin:
            biggestBlowoutMatch = matchup;
            blowoutMargin = abs(matchup.home_score - matchup.away_score)

    if biggestBlowoutMatch.home_score > biggestBlowoutMatch.away_score:
        file.write(biggestBlowoutMatch.home_team.team_name + " blew out " + biggestBlowoutMatch.away_team.team_name
                   + " by " + str(round(blowoutMargin, 2)) + "\n\n")
    else:
        file.write(biggestBlowoutMatch.away_team.team_name + " blew out " + biggestBlowoutMatch.home_team.team_name
                   + " by " + str(round(blowoutMargin, 2)) + "\n\n")

def GetClosestWin(file, boxScores):
    file.write("** THE CLOSEST WIN **\n")
    closestWinMatch = boxScores[0]
    closestWin = 999999
    for matchup in boxScores:
        if (matchup.home_team == 0 or matchup.away_team == 0):
            continue
        if abs(matchup.home_score - matchup.away_score) < closestWin:
            closestWinMatch = matchup;
            closestWin = abs(matchup.home_score - matchup.away_score)

    if closestWinMatch.home_score > closestWinMatch.away_score:
        file.write(closestWinMatch.home_team.team_name + " narrowly beat " + closestWinMatch.away_team.team_name
                   + " by " + str(round(closestWin, 2)) + "\n\n")
    else:
        file.write(closestWinMatch.away_team.team_name + " narrowly beat " + closestWinMatch.home_team.team_name
                   + " by " + str(round(closestWin, 2)) + "\n\n")

def GetBestLuck(file, boxScores):
    bestPercent = -1;
    bestLuckTeamName = ""
    bestLuckTeamProjected = -1
    bestLuckActualScore = -1

    file.write("** THE BEST LUCK **\n")
    for matchup in boxScores:
        if matchup.home_team != 0:
            homeProj = 0;
            for player in matchup.home_lineup:
                if (player.slot_position != "BE" and player.slot_position != "IR"):
                    homeProj += player.projected_points
            if matchup.home_score / homeProj > bestPercent:
                bestPercent = matchup.home_score / homeProj
                bestLuckTeamName = matchup.home_team.team_name
                bestLuckTeamProjected = homeProj
                bestLuckActualScore = matchup.home_score
        if matchup.away_team != 0:
            awayProj = 0;
            for player in matchup.away_lineup:
                if (player.slot_position != "BE" and player.slot_position != "IR"):
                    awayProj += player.projected_points
            if matchup.away_score / awayProj > bestPercent:
                bestPercent = matchup.away_score / awayProj
                bestLuckTeamName = matchup.away_team.team_name
                bestLuckTeamProjected = awayProj
                bestLuckActualScore = matchup.away_score

    file.write(bestLuckTeamName + " was the luckiest team!\nThey were projected to score " + str(round(bestLuckTeamProjected, 2)) + " but scored "
               + str(round(bestLuckActualScore, 2)) + ". Which is " + str(round(bestPercent * 100, 2)) + "% of their projected!\n\n")

def GetWorstLuck(file, boxScores):
    worstPercent = 99999;
    worstLuckTeamName = ""
    worstLuckTeamProjected = -1
    worstLuckActualScore = 9999999

    file.write("** THE WORST LUCK **\n")
    for matchup in boxScores:
        if matchup.home_team != 0:
            homeProj = 0;
            for player in matchup.home_lineup:
                if (player.slot_position != "BE" and player.slot_position != "IR"):
                    homeProj += player.projected_points
            if matchup.home_score / homeProj < worstPercent:
                worstPercent = matchup.home_score / homeProj
                worstLuckTeamName = matchup.home_team.team_name
                worstLuckTeamProjected = homeProj
                worstLuckActualScore = matchup.home_score
        if matchup.away_team != 0:
            awayProj = 0;
            for player in matchup.away_lineup:
                if (player.slot_position != "BE" and player.slot_position != "IR"):
                    awayProj += player.projected_points
            if matchup.away_score / awayProj < worstPercent:
                worstPercent = matchup.away_score / awayProj
                worstLuckTeamName = matchup.away_team.team_name
                worstLuckTeamProjected = awayProj
                worstLuckActualScore = matchup.away_score

    file.write(worstLuckTeamName + " was the unluckiest team :(\nThey were projected to score " + str(round(worstLuckTeamProjected, 2)) + " but scored "
               + str(round(worstLuckActualScore, 2)) + ". Which is " + str(round(worstPercent * 100, 2)) + "% of their projected :(\n\n")



def PerfectRoster(file, boxScores):
    file.write("** PERFECT ROSTERS **\n")
    PerfectRosters = []
    for matchup in boxScores:
        if matchup.home_team != 0 and math.isclose(matchup.home_score, GetOptimalScore(matchup.home_lineup)[0], abs_tol=0.003):
            PerfectRosters.append(matchup.home_team.team_name)
        if matchup.away_team != 0 and math.isclose(matchup.away_score, GetOptimalScore(matchup.away_lineup)[0], abs_tol=0.003):
            PerfectRosters.append(matchup.away_team.team_name)
    if (len(PerfectRosters) == 0):
        file.write("There were no perfect rosters this week.\n\n")
    else:
        file.write("These teams had perfect rosters (max points possible):\n")
        for team in PerfectRosters:
            file.write(team + "\n")
    file.write("\n")

#Change this for your league format
def GetOptimalScore(roster):
    QB = 1;
    RB = 2;
    WR = 2;
    TE = 1;
    FLEX = 1;
    DEF = 1;
    K = 1;
    playerList = []
    bestRoster = []
    bestRosterJustNames = []
    bestScore = 0;
    for player in roster:
        playerList.append((player.points, player))
    playerList.sort(reverse=True, key = lambda x: x[0])

    for player in playerList:
        if "QB" in player[1].eligibleSlots and QB > 0:
            QB -= 1
            bestRoster.append(player)
        elif "RB" in player[1].eligibleSlots and RB > 0:
            RB -= 1
            bestRoster.append(player)
        elif "WR" in player[1].eligibleSlots and WR > 0:
            WR -= 1
            bestRoster.append(player)
        elif "TE" in player[1].eligibleSlots and TE > 0:
            TE -= 1
            bestRoster.append(player)
        elif "RB/WR/TE" in player[1].eligibleSlots and FLEX > 0:
            FLEX -= 1
            bestRoster.append(player)
        elif "D/ST" in player[1].eligibleSlots and DEF > 0:
            DEF -= 1
            bestRoster.append(player)
        elif "K" in player[1].eligibleSlots and K > 0:
            K -= 1
            bestRoster.append(player)

    for player in bestRoster:
        bestScore += player[0]
        bestRosterJustNames.append(player[1].name)

    return (bestScore, bestRosterJustNames)
    



if __name__ == "__main__":

    file = open("WeeklyFantasyWk" + str(WEEK_NUM) + ".txt", "w")

    # you can either make your league public and include the league ID (found in the URL) and year as the first two fields
    # or keep it private and follow this page to find the espn_s2 and swid for the 3rd and 4th params
        league = League(IdHere, YearHere)

    boxScores = league.box_scores(WEEK_NUM)
    
    WriteMatchupScores(file, boxScores)
    GetTopScorers(file, league)
    GetBottomScorers(file, league)
    GetBiggestBlowout(file, boxScores)
    GetClosestWin(file, boxScores)
    GetBestLuck(file, boxScores)
    GetWorstLuck(file, boxScores)
    PerfectRoster(file, boxScores)
    GetBestBench(file, boxScores)
    GetWorstBench(file, boxScores)
    GetUpsets(file, boxScores)
    CouldHaveWonIf(file, boxScores)

    print("Summary complete for week " + str(WEEK_NUM))
    webbrowser.open("WeeklyFantasyWk" + str(WEEK_NUM) + ".txt")
    file.close()
        
