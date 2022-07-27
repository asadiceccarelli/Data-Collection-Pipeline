def valid_clubs():
    '''
    Abbreviates the club name to 3 unique letters.

    Args:
        Club (str): The name of the club to be shortened.

    Returns:
        str: Shortened name.
    '''
    return {
        'Arsenal': 'ARS',
        'Aston Villa': 'AVL',
        'Brentford': 'BRE',
        'Brighton': 'BHA',
        'Burnley': 'BUR',
        'Chelsea': 'CHE',
        'Crystal Palace': 'CRY',
        'Everton': 'EVE',
        'Leeds': 'LEE',
        'Leicester': 'LEI',
        'Liverpool': 'LIV',
        'Man City': 'MCI',
        'Man Utd': 'MUN',
        'Newcastle': 'NEW',
        'Norwich': 'NOR',
        'Southampton': 'SOU',
        'Spurs': 'TOT',
        'Watford': 'WAT',
        'West Ham': 'WHU',
        'Wolves': 'WOL'
    }


def valid_seasons():
    '''
    A list of seasons the premier league website contains information on.

    Returns:
        list: List of valid years
    '''
    return [
        '1992/93', '1993/94', '1994/95', '1995/96', '1996/97',
        '1997/98', '1998/99', '1999/00', '2000/01', '2001/02',
        '2002/03', '2003/04', '2004/05', '2005/06', '2006/07',
        '2007/08', '2008/09', '2009/10', '2010/11', '2011/12',
        '2012/13', '2013/14', '2014/15', '2015/16', '2016/17',
        '2017/18', '2018/19', '2019/20', '2020/21', '2021/22'
    ]