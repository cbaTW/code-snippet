#!/usr/bin/env python3
"""
TODO: Loading Overlay
"""
from flask import render_template, request, make_response, session, redirect, url_for
from flask import current_app as app

from src.util import responses

import asyncio
import aiohttp

from bs4 import BeautifulSoup

import traceback


def cpe2name(cpe):
    tmp = cpe[6:].replace(':', ' ').split(' ')
    try:
        if tmp[0] == tmp[1]:
            tmp = '{} {}'.format(tmp[1], tmp[2])
        else:
            tmp = '{} {} {}'.format(tmp[0], tmp[1], tmp[2])
    except:
        if tmp[0] == tmp[1]:
            tmp = '{}'.format(tmp[1])
        else:
            tmp = '{} {}'.format(tmp[0], tmp[1])
    return tmp


def concat(cve, epss):
    for index1, item1 in enumerate(cve):
        for index2, item2 in enumerate(epss):
            if item1['Name'] == item2['Name']:
                for index11, item11 in enumerate(item1['CVE_data']):
                    for index22, item22 in enumerate(item2['epss_data']):
                        if item11['Title'] == item22['cve']:
                            item11['epss'] = item22['epss']
                            item11['percentile'] = item22['percentile']
                            break
                        else:
                            item11['epss'] = 'N/A'
                            item11['percentile'] = 'N/A'
    return cve


def query_hanle(query):
    tmp = query.replace('\n', ' ').replace('\r', ' ').split(' ')
    while '' in tmp:
        tmp.remove('')
    return tmp


def point2priority(pp):
    if pp > 0 and pp < 4:
        return "Minor"
    elif pp < 7:
        return "Major"
    elif pp < 9:
        return "Critical"
    elif pp < 10:
        return "Blocker"


def cve_search_list_extract(respTEXT):
    results = []
    soup = BeautifulSoup(respTEXT, "html.parser")
    steps = int(soup.find("strong", {"data-testid": "vuln-displaying-count-through"}).text)
    list = soup.select("tbody")[0].find_all("tr")
    for index, item in enumerate(list):
        result = {
            "Title": "",
            "Description": "",
            "Published": "",
            "CVSS3": {
                "Exist": bool,
                "Points": float,
                "Class": '',
                "String": ''
            },
            "CVSS2": {
                "Exist": bool,
                "Points": float,
                "Class": '',
                "String": ''
            },

        }
        anchor = str(index)

        Title = soup.find("a", {"data-testid": "vuln-detail-link-" + anchor}).text
        Summary = soup.find("p", {"data-testid": "vuln-summary-" + anchor}).text
        Published = soup.find("span", {"data-testid": "vuln-published-on-" + anchor}).text

        try:
            cvss3 = soup.find("a", {"data-testid": "vuln-cvss3-link-" + anchor})
            cvss3_tmp = cvss3.text.split(sep=" ")

            cvss3_points = float(cvss3_tmp[0])
            cvss3_class = point2priority(cvss3_points)
            cvss3_tmp = cvss3['href'].find('vector=')
            cvss3_string = cvss3['href'][cvss3_tmp+7 : cvss3_tmp+42]
            result["CVSS3"]["Exist"] = True

        except AttributeError: # No CVSS 3
            cvss3 = soup.find("span", {"data-testid": "vuln-cvss3-na-" + anchor})
            
            cvss3_points = 0
            cvss3_class = 'N/A'
            cvss3_string = 'N/A'
            result["CVSS3"]["Exist"] = False
        
        try:
            cvss2 = soup.find("a", {"data-testid": "vuln-cvss2-link-" + anchor})
            cvss2_tmp = cvss2.text.split(sep=" ")

            cvss2_points = float(cvss2_tmp[0])
            cvss2_class = point2priority(cvss2_points)
            cvss2_tmp = cvss2['href'].find('vector=')
            cvss2_string = cvss2['href'][cvss2_tmp+7 : cvss2_tmp+35]
            result["CVSS2"]["Exist"] = True

        except AttributeError: # No CVSS 3
            cvss2 = soup.find("span", {"data-testid": "vuln-cvss2-na-" + anchor})
            
            cvss2_points = 0
            cvss2_class = 'N/A'
            cvss2_string = 'N/A'
            result["CVSS2"]["Exist"] = False

        result["Title"] = Title
        result["Description"] = Summary
        result["Published"] = Published
        result["CVSS3"]["Points"] = cvss3_points
        result["CVSS3"]["Class"] = cvss3_class
        result["CVSS3"]["String"] = cvss3_string

        result["CVSS2"]["Points"] = cvss2_points
        result["CVSS2"]["Class"] = cvss2_class
        result["CVSS2"]["String"] = cvss2_string
        results.append(result)
    return results 


async def get_rq(url, client, type):
    try:
        if type == 'JSON':
            async with client.get(url) as r:
                return await r.json()
        else:
            async with client.get(url) as r:
                assert r.status == 200
                return await r.text()
    except:
        traceback.print_exc()


async def make_list_and_name(clean_list):
    origin = clean_list
    results = []
    for index, item in enumerate(origin):
        origin[index] = item + "&startIndex=0" if item.find("&startIndex=0") == -1 else item
    
    async with aiohttp.ClientSession() as client:
        task1 = [ get_rq(i, client, 'TEXT') for i in origin]
        task1 = await asyncio.gather(*task1)

    for index, item in enumerate(task1):
        result = {}
        result['Links'] = [ origin[index] ]
        result['Name'] = ''
        soup = BeautifulSoup(item, "html.parser")

        anchor = int(soup.find("strong", {"data-testid": "vuln-matching-records-count"}).text)
        trace = int(anchor / 20) if anchor % 20 == 0 else int(anchor / 20) + 1
        if trace > 1:
            for i in range(1, trace):
                result['Links'].append(origin[index].replace("startIndex=0", "startIndex=" + str(i * 20)))

        try:
            tmp = soup.find("span", {"data-testid": "vuln-params-cpe_version-value"}).text
            result['Name'] = cpe2name(tmp)
        except:
            try:
                tmp = soup.find("span", {"data-testid": "vuln-params-cpe_product-value"}).text
                result['Name'] = cpe2name(tmp)
            except:
                try:
                    tmp = soup.find("span", {"data-testid": "vuln-params-query-value"}).text
                    result['Name'] = tmp
                except:
                    result['Name'] = "Please paste your search url to boan.chen to fix this"
                    pass
                pass
            pass
        results.append(result)
    return results


async def fetch_cve(double_list):
    results = []
    task1 = []
    task1_result = []
    async with aiohttp.ClientSession() as client:
        for index, item in enumerate(double_list):
            task1.append([])
            for i in item['Links']:
                task1[index].append(get_rq(i, client, 'TEXT'))
        for index, item in enumerate(task1):
             task1_result.append([])
             task1_result[index] = await asyncio.gather(*item)
        for index, item in enumerate(task1_result):
            results.append({})
            results[index]['Name'] = double_list[index]['Name']
            results[index]['Link'] = double_list[index]['Links'][0]
            results[index]['CVE_data'] = [ j for i in item for j in cve_search_list_extract(i) ]
    return results


async def fetch_epss(cve_list):
    results = []
    epss_list = []
    for index, item in enumerate(cve_list):
        epss_list.append({})
        epss_list[index]['Name'] = item['Name']
        epss_api = 'https://api.first.org/data/v1/epss?cve='
        for i in item['CVE_data']:
            tmp = i['Title']
            if int(tmp[4:8]) > 2011:
                epss_api += tmp
                epss_api += ','
        epss_list[index]['api_link'] = epss_api

    task1 = []
    async with aiohttp.ClientSession() as client:
        task1 = [ get_rq(i['api_link'], client, 'JSON') for i in epss_list]
        task1 = await asyncio.gather(*task1)

    for index, item in enumerate(task1):
        epss_list[index]['epss_data'] = item['data']

    return epss_list


            

async def go(clean_list):
    double_list = await make_list_and_name(clean_list)
    cve_list = await fetch_cve(double_list)
    epss_list = await fetch_epss(cve_list)
    result = concat(cve_list, epss_list)
    return result

async def cve_formatter():
    """
    Recieve POST request
    """
    result = await go(query_hanle(request.form['url']))

    return responses.set_response(
        make_response(
            render_template("cve.html",
                            version=app.config["VERSION"],
                            result=result,
                            )
        )
    )