
"""
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

import pynmrstar
import pandas as pd
import urllib.request, json

BMRB_API_URL = "http://webapi.bmrb.wisc.edu/v2"
Shift_search_URL = '/search/multiple_shift_search?'
Database ='&database='
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

def bmrbMultiShiftSearch(shifts:list, databaseType=Metabolomics):
  bmrbUrl = BMRB_API_URL+Shift_search_URL
  shiftAsStr = ''
  for shift in shifts:
    shiftAsStr += S + str(shift) + AND
  fullUrl = bmrbUrl+shiftAsStr+Database+databaseType
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
  ala = [3.771,1.471]
  df = bmrbMultiShiftSearch(ala)
  print(df[Title], df[PeaksMatched])



