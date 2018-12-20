"""
Module Documentation here
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:55 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-03-23 16:50:22 +0000 (Thu, March 23, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

tempQueryCode = """
Below the script from BMRB website.
Copied for understanding how it worked only.

 history.replaceState('data', '', '/search/multiple_peak_search.php?' + $("#search_form").serialize());
    $("#loading").show();
    $("#results").hide();
    $("body").css("cursor", "progress");

    $("#shift_body").empty();

    // Make the parameter data packet
    var data = {
        s: shifts,
        database: $('#database').val()
    }


    // Perform the query
    $.ajax({
        type: "get",
        data: data,
        traditional: true,
        url: "http://webapi.bmrb.wisc.edu/v2/search/multiple_shift_search",
        success: function(response){

            $("#loading").hide();
            $("body").css("cursor", "default");

            if (response["data"].length == 0){
                alert("No matching peaks found.");
                return;
            }

            $.each(response["data"], function(i, item) {
                $('<tr>').append(
                    $('<td>').append($('<a>',{text: item.Entry_ID, title: item.Entry_ID, href: item.Link})),
                    $('<td>').text(item.Title),
                    $('<td>').text(item.Peaks_matched),
                    $('<td>').text(item.Combined_offset),
                    $('<td>').text(item.Assigned_chem_shift_list_ID),
                    $('<td>').text(item.Val.join(", "))
                ).appendTo('#shifts_table');
            });

            $("#results").show();
        }, error: function(xhr){
            $("#loading").hide();
            $("body").css("cursor", "default");
            alert($.parseJSON(xhr.responseText)["error"]);
        }
    });

"""

# import pynmrstar
import pandas as pd
import urllib.request, json


BMRB_API_URL = "http://webapi.bmrb.wisc.edu/v2"
Shift_search_URL = '/search/multiple_shift_search?'
Database = '&database='
Metabolomics = 'metabolomics'
AND = '&'
S = 's='

csData = 'data'
# DataFrame column titles from BMRB database
Title = 'Title'
EntryID = 'Entry_ID'
AssignedshiftID = 'Assigned_chem_shift_list_ID'
CombinedOffset = 'Combined_offset'
ShiftLink = 'Link'
PeaksMatched = 'Peaks_matched'

ShiftColumns = [
    AssignedshiftID,
    CombinedOffset,
    EntryID,
    ShiftLink,
    PeaksMatched,
    Title,
    ]
"""
Full address to be: 

  - for a single chemical shift query (e.g. 3.136), database=metabolomics
    >> "http://webapi.bmrb.wisc.edu/v2/search/multiple_shift_search?s=3.136&database=metabolomics"
  
  - for multiple  chemical shift searches (e.g. 3.136,7):
    >> "http://webapi.bmrb.wisc.edu/v2/search/multiple_shift_search?s=3.136&s=7.0&database=metabolomics"

"""


def bmrbMultiShiftSearch(shifts: list, databaseType=Metabolomics):
    bmrbUrl = BMRB_API_URL + Shift_search_URL
    shiftAsStr = ''
    for shift in shifts:
        shiftAsStr += S + str(shift) + AND
    fullUrl = bmrbUrl + shiftAsStr + Database + databaseType
    with urllib.request.urlopen(fullUrl) as url:
        data = json.loads(url.read().decode())
        d = data[csData]
        df = pd.DataFrame.from_dict(d)
    return d


def peaksToShifts1D(objs):
    '''
    :param objs: peaks or multiplets
    :return: a list of peak positions
    '''
    return [x.position[0] for x in objs]


def testAla():
    ala = [3.771, 1.471]
    df = bmrbMultiShiftSearch(ala)
    print(df[Title], df[PeaksMatched])
