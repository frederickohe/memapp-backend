"""Seed prominent YMCA figures shown on the member dashboard."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

import utilities.dbmodels  # noqa: F401

from core.dashboard.model.ProminentProfile import ProminentProfile
from utilities.dbconfig import SessionLocal

WIKI = "https://upload.wikimedia.org/wikipedia/commons"

PROFILES = [
    {
        "id": "PROF_Kufuor0001",
        "full_name": "John Agyekum Kufuor",
        "headline": "Former President of Ghana and YMCA member",
        "occupation": "Statesman",
        "country": "Ghana",
        "era": "1938 – Present",
        "category": "GHANA",
        "sort_order": 1,
        "photo_url": f"{WIKI}/thumb/6/63/John_Kufuor_080915-A-8817J-090.JPG/640px-John_Kufuor_080915-A-8817J-090.JPG",
        "bio": """John Kofi Agyekum Kufuor served as President of Ghana from 2001 to 2009 and later as Chairperson of the African Union. He has spoken openly about the Ghana YMCA as one of the institutions that shaped his sense of responsibility and leadership.

In public remarks, he recalled the Association in the 1950s as a transformational centre that prepared young people to face leadership challenges. His association with the movement is often cited by Ghana YMCA as an example of how membership can form national leaders.

Kufuor’s presidency marked Ghana’s first democratic transfer of power from one elected party to another. For YMCA members, his story connects youth formation, public service, and the long tradition of civic leadership in the Ghana movement.""",
    },
    {
        "id": "PROF_Coffie0001",
        "full_name": "George Dela Coffie",
        "headline": "National President of Ghana YMCA",
        "occupation": "National President",
        "country": "Ghana",
        "era": "Present",
        "category": "GHANA",
        "sort_order": 2,
        "photo_url": "https://www.myjoyonline.com/wp-content/uploads/2026/08/IMG_1759.JPG-1024x630.jpeg",
        "bio": """George Dela Coffie was elected National President of the Ghana Young Men’s Christian Association at its 4th Quadrennial National Council Meeting in Accra.

A former Ashanti Regional Vice President, he was chosen by 33 accredited delegates after a transparent vetting and election process. He leads the Association for a four-year term alongside Rev. Alex Owusu Addo (National Vice President), Sarah Mamle Kodjie (National Women’s Commissioner), and Frederick Obuo Ohene (National Treasurer).

His election came as Ghana YMCA received global recognition, including the 2026 World YMCA Impact Award in the Meaningful Work category. He now steers the national movement’s next chapter of youth empowerment, skills development, and community impact.""",
    },
    {
        "id": "PROF_Williams01",
        "full_name": "Sir George Williams",
        "headline": "Founder of the YMCA",
        "occupation": "Philanthropist and businessman",
        "country": "England",
        "era": "1821 – 1905",
        "category": "WORLD",
        "sort_order": 3,
        "photo_url": f"{WIKI}/thumb/c/c3/Sir_George_Williams_by_John_Collier.jpg/640px-Sir_George_Williams_by_John_Collier.jpg",
        "bio": """Sir George Williams founded the Young Men’s Christian Association in London on 6 June 1844. Born in Somerset, England, he moved to London as a draper’s apprentice and lived among the many young working men crowded into the city.

Appalled by the conditions those young men faced, Williams gathered eleven fellow drapers and created a place for Bible study, prayer, and mutual improvement. That small gathering became the oldest and largest youth movement in the world.

Williams was knighted by Queen Victoria in 1894. After his death in 1905 he was commemorated with a stained-glass window in Westminster Abbey and buried in St Paul’s Cathedral. Every YMCA, including Ghana YMCA, traces its beginning to his vision.""",
    },
    {
        "id": "PROF_Sanvee0001",
        "full_name": "Carlos Madjri Sanvee",
        "headline": "Secretary General of the World YMCA",
        "occupation": "Secretary General, World Alliance of YMCAs",
        "country": "Togo",
        "era": "2019 – Present",
        "category": "WORLD",
        "sort_order": 4,
        "photo_url": "https://www.ymca.int/wp-content/uploads/2024/02/3.png",
        "bio": """Carlos Madjri Sanvee of Togo is Secretary General of the World Alliance of YMCAs, the first African to hold the role. Elected in 2018, he took office in January 2019 and leads a movement reaching more than 65 million people in over 120 countries.

He began as a teenage volunteer with YMCA Togo, joined staff in 1987, and later served as Deputy National General Secretary. He spent a decade as General Secretary of the African Alliance of YMCAs in Nairobi before moving to the World Alliance in Geneva.

Under his leadership the movement launched Vision 2030, the COVID Solidarity Fund, and youth-led solutions work. For African members, his story is proof that local YMCA service can lead to global leadership.""",
    },
    {
        "id": "PROF_AbbeyGhana",
        "full_name": "Wilkins Miccaber Abbey",
        "headline": "Founder of the Ghana YMCA",
        "occupation": "YMCA pioneer",
        "country": "Ghana",
        "era": "1890",
        "category": "GHANA",
        "sort_order": 5,
        "photo_url": None,
        "bio": """Wilkins Miccaber Abbey introduced the YMCA to the Gold Coast in 1890 after encountering the Association during a study tour in Scotland. He started the work in Accra, first known as the Accra United YMCA, making Ghana YMCA one of the earliest voluntary organisations in the country.

In the same period, Bremen Missions in Togoland were encouraging YMCA groups attached to churches and missions. Those early associations did not yet form a single national movement, but Abbey’s initiative planted the seed.

From that beginning the Ghana YMCA grew through wartime service, post-war partnership with Britain, Germany and the United States, and full membership of the World Alliance of YMCAs in 1961. Abbey remains the founding figure of the Ghana movement.""",
    },
    {
        "id": "PROF_Dunant0001",
        "full_name": "Henry Dunant",
        "headline": "Founder of YMCA Geneva and the Red Cross",
        "occupation": "Humanitarian",
        "country": "Switzerland",
        "era": "1828 – 1910",
        "category": "WORLD",
        "sort_order": 6,
        "photo_url": f"{WIKI}/thumb/3/38/Henry_Dunant-young.jpg/640px-Henry_Dunant-young.jpg",
        "bio": """Henry Dunant, born in Geneva on 8 May 1828, co-founded the YMCA of Geneva in 1852 and became a driving force behind the international YMCA Movement. He organised prayer groups as a young man, then corresponded with associations in nearly thirty towns and travelled to promote the work across Europe and North Africa.

When Paris YMCA leaders proposed a limited francophone meeting, Dunant pressed for a truly international gathering. His insistence helped bring about the first International YMCA Conference in Paris in 1855, which established the World Alliance of YMCAs.

Dunant later founded the International Committee of the Red Cross and received the first Nobel Peace Prize in 1901. His life shows how YMCA service and humanitarian leadership have long been intertwined.""",
    },
    {
        "id": "PROF_Naismith01",
        "full_name": "James Naismith",
        "headline": "Invented basketball at the YMCA",
        "occupation": "Physical educator",
        "country": "Canada",
        "era": "1861 – 1939",
        "category": "WORLD",
        "sort_order": 7,
        "photo_url": f"{WIKI}/thumb/4/4a/Dr._James_Naismith.jpg/640px-Dr._James_Naismith.jpg",
        "bio": """James Naismith, a Canadian physical educator, invented basketball in December 1891 while working at the International YMCA Training School in Springfield, Massachusetts — later Springfield College.

Dr Luther Gulick, director of physical education, asked students for an indoor game that could keep young men active in winter. Naismith wrote thirteen rules and used peach baskets as goals. The game spread rapidly through the YMCA network and became an Olympic sport.

Naismith was also a physician, chaplain, and coach. Basketball remains one of the YMCA’s most visible gifts to the world, played today by millions of young people including members across Ghana.""",
    },
    {
        "id": "PROF_Addae00001",
        "full_name": "Kwabena Nketia Addae",
        "headline": "Executive Director of Ghana YMCA",
        "occupation": "Executive Director",
        "country": "Ghana",
        "era": "Present",
        "category": "GHANA",
        "sort_order": 8,
        "photo_url": None,
        "bio": """Kwabena Nketia Addae is Executive Director of Ghana YMCA, succeeding a line of national general secretaries that began with educationist Charles Amaning.

He leads the professional staff of the Association from its national headquarters in Adabraka, Accra. Under this era of leadership Ghana YMCA has advanced programmes such as Youth Justice, Smart Girl, Green Ideas, and the Media Hub Education Centre, and received the 2026 World YMCA Impact Award.

Addae represents the movement with international partners including CVJM Westbund, Bread for the World, and YWCA-YMCA Sweden, while overseeing branches, schools, and technical training centres that serve young people across Ghana.""",
    },
    {
        "id": "PROF_JohnRMott1",
        "full_name": "John R. Mott",
        "headline": "World YMCA President and Nobel Peace Prize laureate",
        "occupation": "YMCA and ecumenical leader",
        "country": "United States",
        "era": "1865 – 1955",
        "category": "WORLD",
        "sort_order": 9,
        "photo_url": f"{WIKI}/thumb/a/aa/John_Raleigh_Mott.jpg/640px-John_Raleigh_Mott.jpg",
        "bio": """John Raleigh Mott was an American evangelist and one of the most influential YMCA leaders of the twentieth century. As a student at Cornell University he served as president of the campus YMCA, then spent 27 years as Secretary of the Intercollegiate YMCA of the USA and Canada.

From 1915 to 1928 he was General Secretary of the International YMCA Committee, and from 1926 to 1937 President of the World Alliance of YMCAs. He also helped found the World Student Christian Federation in 1895 and later the World Council of Churches.

Mott received the Nobel Peace Prize in 1946 for drawing together people of many nations and communions in a common spiritual bond. His career is a model of student YMCA leadership growing into global peacemaking.""",
    },
    {
        "id": "PROF_Habiah0001",
        "full_name": "Charles Habiah",
        "headline": "Former National President of Ghana YMCA",
        "occupation": "Lawyer and National President",
        "country": "Ghana",
        "era": "Recent",
        "category": "GHANA",
        "sort_order": 10,
        "photo_url": None,
        "bio": """Charles Habiah Esq. served as National President of Ghana YMCA, continuing a line of national chairmen that includes Hon. K. Amoa-Awuah, Kwame Gyimah-Akwafo, and Prof. Emmanuel Larbi Kwame Osafo.

A lawyer by profession, he led the Association through a period of programme expansion, partnership building, and preparation for the next quadrennial leadership cycle. His tenure sits in the same national leadership tradition that later elected George Dela Coffie as National President.

Ghana YMCA remembers Habiah among the high-profile personalities who have served the movement as volunteers, leaders, and management staff.""",
    },
    {
        "id": "PROF_WGMorgan01",
        "full_name": "William G. Morgan",
        "headline": "Invented volleyball at the YMCA",
        "occupation": "YMCA physical director",
        "country": "United States",
        "era": "1870 – 1942",
        "category": "WORLD",
        "sort_order": 11,
        "photo_url": f"{WIKI}/thumb/7/78/William_G._Morgan.jpg/640px-William_G._Morgan.jpg",
        "bio": """William George Morgan invented volleyball in 1895 while serving as physical director of the YMCA in Holyoke, Massachusetts. He wanted a game with less physical contact than basketball, suitable for businessmen and older members in his classes.

He mixed elements of basketball, baseball, tennis, and handball, first calling the sport “Mintonette.” A net 6 feet 6 inches high — just taller than the average man of the time — defined the court. The game was soon renamed volleyball and spread through the YMCA network across the Americas and then the world.

By the 1950s it was played by tens of millions of people. Volleyball became an Olympic sport in 1957. Like basketball, it is a YMCA invention that still shapes sport and recreation in Ghana and worldwide.""",
    },
    {
        "id": "PROF_AmoaAwuah1",
        "full_name": "K. Amoa-Awuah",
        "headline": "First National Chairman of Ghana YMCA",
        "occupation": "Deputy Minister of Health and National Chairman",
        "country": "Ghana",
        "era": "Independence era",
        "category": "GHANA",
        "sort_order": 12,
        "photo_url": None,
        "bio": """The late Hon. K. Amoa-Awuah was the first National Chairman of Ghana YMCA. At the time he also served as Deputy Minister of Health in the government of Osagyefo Dr Kwame Nkrumah.

His leadership came as the Association moved from scattered local groups into a national movement, with headquarters in Accra and regional secretaries across Greater Accra, Ashanti, Brong Ahafo, Western, Central, Eastern, and Volta.

Amoa-Awuah’s dual role in public office and YMCA leadership set a pattern that Ghana YMCA still celebrates: high-profile personalities serving as volunteers, board leaders, and advocates for young people.""",
    },
    {
        "id": "PROF_Amaning001",
        "full_name": "Charles Amaning",
        "headline": "First National General Secretary of Ghana YMCA",
        "occupation": "Educationist and General Secretary",
        "country": "Ghana",
        "era": "National founding years",
        "category": "GHANA",
        "sort_order": 13,
        "photo_url": None,
        "bio": """Charles Amaning, an educationist, was the first National General Secretary of Ghana YMCA. He built the professional secretariat that turned a collection of local associations into a coordinated national movement.

He was succeeded by Emmanuel A. Boateng, then Samuel Edmund Nyame, Alfred A. Sarkodie, Samuel Henry Edward Anim, Prosper Hoeyi, and today’s Executive Director, Kwabena Nketia Addae.

Amaning’s work sits behind the later expansion of vocational training, rural development, kindergartens, and youth leadership programmes that still define Ghana YMCA.""",
    },
    {
        "id": "PROF_GyimahAkwa",
        "full_name": "Kwame Gyimah-Akwafo",
        "headline": "Former National President of Ghana YMCA",
        "occupation": "National President",
        "country": "Ghana",
        "era": "Recent decades",
        "category": "GHANA",
        "sort_order": 14,
        "photo_url": None,
        "bio": """Kwame Gyimah-Akwafo served as National President of Ghana YMCA and is remembered among the Association’s high-profile national chairmen.

During his leadership he articulated the movement’s vision of empowering young people in Ghana for the African renaissance — the same vision Ghana YMCA still carries as a member of the African Alliance of YMCAs.

He hosted and spoke at national events that connected YMCA formation with public leadership, including occasions attended by former President John Agyekum Kufuor. His tenure is part of the leadership chain that runs from Hon. K. Amoa-Awuah to the present National President.""",
    },
]


def seed():
    db = SessionLocal()
    created = 0
    updated = 0
    try:
        for item in PROFILES:
            existing = db.query(ProminentProfile).filter(ProminentProfile.id == item["id"]).first()
            if existing:
                for key, value in item.items():
                    if key != "id":
                        setattr(existing, key, value)
                existing.is_published = True
                updated += 1
            else:
                db.add(ProminentProfile(is_published=True, **item))
                created += 1
        db.commit()
        print(f"Prominent profiles seed complete: created={created}, updated={updated}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
