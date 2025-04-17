import re
import requests
import xml.etree.ElementTree as ET
from utils.xml_parser import parse_law_xml
import streamlit as st

OC = "chetera"
BASE = "http://www.law.go.kr"

def fetch_law_list_and_detail(query, unit):
    try:
        from urllib.parse import quote
        encoded_query = quote(query)
        url = f"{BASE}/DRF/lawSearch.do?OC={OC}&target=law&type=XML&display=10&search=2&knd=A0002&query={encoded_query}"
        res = requests.get(url)
        res.encoding = "utf-8"

        if res.status_code != 200:
            st.error(f"🚨 목록 요청 실패 (코드 {res.status_code})")
            return []

        try:
            root = ET.fromstring(res.content)
        except ET.ParseError as e:
            st.error(f"🚨 XML 파싱 오류: {e}")
            return []

        terms = [t.strip() for t in re.split(r"[,&\-()]", query or "") if t.strip()]
        results = []

        for law in root.findall("law"):
            name = law.findtext("법령명한글", "").strip()
            mst = law.findtext("법령일련번호", "").strip()
            detail = law.findtext("법령상세링크", "").strip()
            full_link = BASE + detail
            xml_data = fetch_law_xml_by_mst(mst)
            if xml_data:
                articles = parse_law_xml(xml_data, terms, unit)
                if articles:
                    results.append({
                        "법령명한글": name,
                        "원문링크": full_link,
                        "조문": articles
                    })
        return results
    except Exception as e:
        st.error(f"🚨 검색 중 예외 발생: {e}")
        return []

def fetch_law_xml_by_mst(mst):
    url = f"http://www.law.go.kr/DRF/lawService.do?OC={OC}&target=law&type=XML&mst={mst}"
    res = requests.get(url)
    res.encoding = "utf-8"
    if res.status_code != 200:
        return None
    return res.text
