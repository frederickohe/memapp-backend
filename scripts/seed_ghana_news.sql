-- Seed published news from https://ymcaghana.org/
-- Impact stories appear on the member dashboard Impact Stories section.

INSERT INTO news (
  id, admin_id, title, content, summary, content_type, is_impact_story,
  event_date, event_location, is_published, created_at, updated_at, published_at
) VALUES
(
  'NEWS_ImpactAward1',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Wins Global Impact Award at 21st World YMCA Council in Toronto',
  $c$Ghana YMCA has been named the winner of the 2026 World YMCA Impact Award in the Meaningful Work category, earning global recognition for its outstanding contribution to youth empowerment through innovative skills development.

The prestigious award was presented during the 21st World YMCA Council in Toronto, Canada, where more than 1,300 delegates from over 100 countries gathered to celebrate transformative initiatives from across the global YMCA Movement.

Ghana YMCA received the award for its flagship initiative, Resilient Africa: Training in Filmmaking and Media for Peace, a programme that equips young people with practical filmmaking, digital storytelling and media production skills while promoting peacebuilding, social cohesion and sustainable livelihoods. Through the initiative, thousands of young people have acquired industry-relevant skills, creating pathways to employment, entrepreneurship and social impact within the creative economy.

The World YMCA Impact Awards recognize projects that demonstrate measurable impact while advancing the objectives of YMCA Vision 2030. This year’s awards attracted 70 project submissions from YMCAs across the world, with only 16 projects shortlisted. Ghana YMCA emerged as the winner in the Meaningful Work category.

Ghana YMCA expressed profound appreciation to its development partner, Bread for the World, whose financial and technical support has been instrumental in the implementation and expansion of the Resilient Africa initiative.$c$,
  'Ghana YMCA won the 2026 World YMCA Impact Award in Meaningful Work at the 21st World YMCA Council in Toronto for the Resilient Africa filmmaking programme.',
  'NEWS', true, NULL, NULL, true,
  '2026-08-06 12:00:00+00', '2026-08-06 12:00:00+00', '2026-08-06 12:00:00+00'
),
(
  'NEWS_PresidentElc',
  'ymD3MaEjEkbOmtxv8fye',
  'George Dela Coffie elected President of Ghana YMCA at 4th Quadrennial Council Meeting',
  $c$Mr. George Dela Coffie has been elected National President of the Ghana Young Men’s Christian Association (YMCA) at its 4th Quadrennial National Council Meeting held at the organization’s National Headquarters in Accra.

The meeting brought together YMCA leaders, delegates, partners and other stakeholders to review the Association’s progress over the past four years and set priorities for the next quadrennial period. After fulfilling all electoral requirements, 33 accredited delegates exercised their franchise in a transparent, credible and peaceful election.

Mr. Coffie, a former Ashanti Regional Vice President, will lead the Ghana YMCA for the next four years. Rev. Alex Owusu Addo was elected National Vice President, while Ms. Sarah Mamle Kodjie and Mr. Frederick Obuo Ohene were elected National Women’s Commissioner and National Treasurer, respectively.

The Council Meeting was attended by distinguished guests including Ms. Lantonirina Rakotomalala, General Secretary of the African Alliance of YMCAs, and partners from Sierra Leone and Kenya. Members, staff and delegates pledged their support to the newly elected National Officers.$c$,
  'George Dela Coffie was elected National President at Ghana YMCA’s 4th Quadrennial National Council Meeting in Accra.',
  'NEWS', false, NULL, NULL, true,
  '2026-08-25 10:00:00+00', '2026-08-25 10:00:00+00', '2026-08-25 10:00:00+00'
),
(
  'NEWS_SmartGirl001',
  'ymD3MaEjEkbOmtxv8fye',
  'Smart Girl Project empowers girls through menstrual health, confidence and leadership',
  $c$Smart Girl is a dignity-centered empowerment project designed to ensure that girls and women in deprived rural communities manage menstruation safely, confidently, and without stigma.

Implemented by YMCA Ghana in partnership with CVJM Westbund, the project responds to period poverty, menstrual stigma, and limited access to hygiene products and information. It aligns with SDG 5 on Gender Equality, SDG 3 on Good Health and Well-being, and SDG 4 on Quality Education.

The project provides menstrual hygiene products, community sensitization workshops, peer educator training, and the Dial Pad Initiative, which establishes pad banks in selected communities. Boys and men are also engaged so communities can reduce stigma and support girls to stay in school.

At its core, Smart Girl is about restoring dignity, promoting gender equality, and creating supportive communities where girls and women thrive.$c$,
  'The Smart Girl Project provides menstrual health education, hygiene support and leadership training for girls across Ghana.',
  'NEWS', true, NULL, NULL, true,
  '2026-06-15 12:00:00+00', '2026-06-15 12:00:00+00', '2026-06-15 12:00:00+00'
),
(
  'NEWS_YouthJustic1',
  'ymD3MaEjEkbOmtxv8fye',
  'Youth Justice III restores hope for vulnerable young people across Ghana',
  $c$Youth Justice III is a youth-centered justice and resilience initiative designed to restore hope, dignity, and opportunity to young people in conflict with the law, youth at risk, and young ex-detainees in Ghana.

Implemented by the Ghana YMCA in partnership with the YWCA-YMCA Sweden and supported by SIDA and SMC, the project equips youth with psychosocial support, life skills, mentorship, vocational training and reintegration opportunities.

Across Greater Accra, Ashanti, Eastern and Volta Regions, the programme has delivered legal awareness, counselling, aquaculture and vocational skills, sports, and family reintegration support. Ghana YMCA works with the Ghana Prisons Service, Department of Social Welfare, Ghana Police Service, National Youth Authority and local assemblies.

The impact has been transformational: young ex-detainees have returned to school, gained admissions into tertiary and vocational programmes, and rebuilt their lives as active citizens.$c$,
  'Youth Justice III supports at-risk youth and ex-detainees with rehabilitation, skills training and reintegration across four regions of Ghana.',
  'NEWS', true, NULL, NULL, true,
  '2026-04-20 12:00:00+00', '2026-04-20 12:00:00+00', '2026-04-20 12:00:00+00'
),
(
  'NEWS_GreenIdeas01',
  'ymD3MaEjEkbOmtxv8fye',
  'Green Ideas empowers youth to lead climate action in their communities',
  $c$Green Ideas is a youth-led climate movement designed to empower young Africans to become active changemakers in the fight against climate change.

Implemented by the African Alliance of YMCAs in collaboration with YMCA Ghana and YMCA Madagascar, and funded by the YWCA-YMCA of Sweden, the project equips young people with practical climate knowledge, mentorship, and Human Design Thinking skills.

Through community engagement, clean-up campaigns, urban farming, and recycling initiatives, Green Ideas is raising a new generation of youth climate ambassadors. Schools have adopted environmentally friendly practices, communities have embraced cleaner waste disposal habits, and local initiatives such as rooftop farming have improved food security and resilience.

Green Ideas lives up to its mission: empowering young people to transform climate concerns into community-driven solutions.$c$,
  'Green Ideas trains young climate ambassadors in Ghana to lead clean-ups, recycling, urban farming and community environmental action.',
  'NEWS', true, NULL, NULL, true,
  '2026-05-10 12:00:00+00', '2026-05-10 12:00:00+00', '2026-05-10 12:00:00+00'
),
(
  'NEWS_Resilience01',
  'ymD3MaEjEkbOmtxv8fye',
  'Resilience Africa equips young filmmakers for careers in Ghana’s creative industry',
  $c$The Resilience Africa Film Project is a youth empowerment and creative industry development programme designed to equip young people with practical filmmaking skills, entrepreneurial knowledge, and meaningful employment opportunities.

Implemented by Ghana YMCA with support from Bread for the World, the project addresses barriers that prevent talented young people from accessing quality film education, particularly those in rural communities and low-income households.

Participants acquire skills in documentary and fiction filmmaking, cinematography, editing, lighting, sound production, creative producing, media for peace, and storytelling. The programme also integrates entrepreneurship and employability so graduates can establish film businesses, secure internships, and generate sustainable income.

This flagship initiative underpins Ghana YMCA’s 2026 World YMCA Impact Award in the Meaningful Work category.$c$,
  'Resilience Africa trains young Ghanaians in filmmaking, storytelling and creative entrepreneurship with support from Bread for the World.',
  'NEWS', true, NULL, NULL, true,
  '2026-06-01 12:00:00+00', '2026-06-01 12:00:00+00', '2026-06-01 12:00:00+00'
),
(
  'NEWS_FilmSchool01',
  'ymD3MaEjEkbOmtxv8fye',
  'Digital Film School Africa opens filmmaking education without borders',
  $c$Digital Film School Africa is a digital-first film education programme co-hosted by YMCA Ghana and the African University of Communications and Business (AUCB), in partnership with WELTFILME e.V. and funded by GIZ/BMZ.

The school offers practical, accredited training in screenwriting, documentary filmmaking, cinematography, editing, sound and creative producing. It is designed so young Africans can learn from anywhere, connecting students and instructors beyond borders.

DFS Africa responds to the high cost and limited availability of film schools on the continent. Special emphasis is placed on supporting women in film, giving them equal opportunities to learn, practice, and thrive in the media space.

The programme prepares students for industry pathways while rooting the learning experience in Africa’s cultural context.$c$,
  'Digital Film School Africa offers online, accredited filmmaking courses for young people across the continent, hosted by Ghana YMCA and AUCB.',
  'NEWS', false, NULL, NULL, true,
  '2026-05-20 12:00:00+00', '2026-05-20 12:00:00+00', '2026-05-20 12:00:00+00'
),
(
  'NEWS_EarthDay0001',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Statement on International Mother Earth Day',
  $c$On International Mother Earth Day, Ghana YMCA reaffirmed its commitment to environmental stewardship and youth-led climate action.

Through programmes such as Green Ideas, the Association continues to equip young people with the knowledge and tools to protect their communities, restore local ecosystems, and advocate for a sustainable planet in line with World YMCA Vision 2030.

Ghana YMCA called on members, volunteers, partners and young people to take practical climate action in their branches and communities — from tree planting and clean-up campaigns to recycling and urban farming.

The Association remains committed to raising a generation of climate-conscious leaders who will safeguard Ghana’s natural resources for the future.$c$,
  'Ghana YMCA marked International Mother Earth Day by calling members to youth-led climate action through programmes such as Green Ideas.',
  'NEWS', false, NULL, NULL, true,
  '2025-07-17 12:00:00+00', '2025-07-17 12:00:00+00', '2025-07-17 12:00:00+00'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO news_media (id, news_id, url, media_type, "order") VALUES
('MEDIA_ImpactAward1', 'NEWS_ImpactAward1', 'https://ymcaghana.org/wp-content/uploads/2026/08/WhatsApp-Image-2026-07-23-at-10.41.38-PM-1.jpeg', 'IMAGE', 0),
('MEDIA_PresidentElc', 'NEWS_PresidentElc', 'https://ymcaghana.org/wp-content/uploads/2026/08/WhatsApp-Image-2026-08-25-at-8.37.14-AM-1024x768.jpeg', 'IMAGE', 0),
('MEDIA_SmartGirl001', 'NEWS_SmartGirl001', 'https://ymcaghana.org/wp-content/uploads/2026/06/smart.jpg', 'IMAGE', 0),
('MEDIA_YouthJustic1', 'NEWS_YouthJustic1', 'https://ymcaghana.org/wp-content/uploads/2026/04/Youth-Justice-iii.jpg', 'IMAGE', 0),
('MEDIA_GreenIdeas01', 'NEWS_GreenIdeas01', 'https://ymcaghana.org/wp-content/uploads/2026/06/green.jpg', 'IMAGE', 0),
('MEDIA_Resilience01', 'NEWS_Resilience01', 'https://ymcaghana.org/wp-content/uploads/2026/06/Resilience-Africa-cover2.jpg', 'IMAGE', 0),
('MEDIA_FilmSchool01', 'NEWS_FilmSchool01', 'https://ymcaghana.org/wp-content/uploads/2026/05/dfs-1024x683.jpg', 'IMAGE', 0),
('MEDIA_EarthDay0001', 'NEWS_EarthDay0001', 'https://ymcaghana.org/wp-content/uploads/2025/07/mother.jpg', 'IMAGE', 0)
ON CONFLICT (id) DO NOTHING;

INSERT INTO news (
  id, admin_id, title, content, summary, content_type, is_impact_story,
  event_date, event_location, is_published, created_at, updated_at, published_at
) VALUES
(
  'NEWS_BritishCoun1',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Leadership Pays Courtesy Visit to British Council',
  $c$The National President of the Ghana YMCA, Mr. George Dela Coffie, together with the Executive Director, Mr. Kwabena Nketia Addae, and the National Programmes Director, Mr. Samuel Asamoah, paid a courtesy visit to the Country Director of the British Council, Mr. Nii Doodo Dodoo.

The visit focused on strengthening collaboration and exploring opportunities for strategic partnership between Ghana YMCA and the British Council, particularly in areas that advance youth development and empowerment.

Ghana YMCA remains committed to building strong partnerships that create meaningful opportunities and lasting impact for young people and communities.$c$,
  'National President George Dela Coffie, Executive Director Kwabena Nketia Addae, and Programmes Director Samuel Asamoah visited the British Council in Accra.',
  'NEWS', false, NULL, NULL, true,
  '2026-09-04 12:00:00+00', '2026-09-04 12:00:00+00', '2026-09-04 12:00:00+00'
),
(
  'NEWS_YouthConf001',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Holds 23rd National Youth Conference in Takoradi',
  $c$Young people from branches across Ghana gathered in Takoradi for the 23rd National Youth Conference, a flagship gathering of fellowship, leadership formation, and service.

Delegates took part in plenaries, workshops, worship, and community outreach. The conference renewed the movement’s call for youth to lead with integrity and to carry practical projects back to their regions.

Ghana YMCA thanked host branches in the Western Region, partners, and volunteers who made the week possible.$c$,
  'Delegates from across Ghana met in Takoradi for the 23rd National Youth Conference, a week of leadership, fellowship, and service.',
  'NEWS', true, NULL, NULL, true,
  '2026-09-09 12:00:00+00', '2026-09-09 12:00:00+00', '2026-09-09 12:00:00+00'
),
(
  'NEWS_CVJMInterns1',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Welcomes Two Interns from CVJM Westbund',
  $c$Ghana YMCA has welcomed two interns from long-standing partner CVJM Westbund. The interns will serve alongside staff and volunteers at national headquarters and selected branches.

The exchange continues a partnership that has supported programmes such as Smart Girl and youth leadership development. During their stay the interns will learn from Ghana YMCA’s community work and share experiences from the German YMCA movement.

Members are invited to greet the visitors at branch activities and help them feel at home.$c$,
  'Two interns from partner movement CVJM Westbund have arrived to serve with Ghana YMCA staff and branches.',
  'NEWS', false, NULL, NULL, true,
  '2026-08-26 12:00:00+00', '2026-08-26 12:00:00+00', '2026-08-26 12:00:00+00'
),
(
  'NEWS_ClinicDonat1',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Donates Medical Equipment to YMCA Clinic at Akpafu Odomi',
  $c$Ghana YMCA has donated medical equipment and essential supplies to the YMCA clinic at Akpafu Odomi, strengthening healthcare access for families in the community.

The donation is part of the Association’s long commitment to community wellbeing — standing with local health workers, volunteers, and partners to keep clinics stocked and welcoming.

Branch members joined the presentation and pledged continued support for the clinic’s outreach to mothers, children, and older residents.$c$,
  'Ghana YMCA delivered medical equipment and supplies to the YMCA clinic at Akpafu Odomi to support community healthcare.',
  'NEWS', true, NULL, NULL, true,
  '2025-10-08 12:00:00+00', '2025-10-08 12:00:00+00', '2025-10-08 12:00:00+00'
),
(
  'NEWS_NuhuFamily01',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Has Given Me a Family I Can Rely On Forever — Nuhu',
  $c$Nuhu, a Ghana YMCA member, says the Association gave him a family he can rely on. Through branch life, mentoring, and programmes, he found belonging, skills, and people who walked with him through difficult seasons.

His story is one of many across the movement: young people who arrive looking for a place to grow and stay because they are seen, trusted, and sent out to serve.

Ghana YMCA continues to open that same door — in Accra, Kumasi, Takoradi, Ho, Koforidua, and communities beyond the regional centres.$c$,
  'Member Nuhu shares how Ghana YMCA became a family, offering belonging, mentoring, and a place to grow.',
  'NEWS', true, NULL, NULL, true,
  '2025-08-20 12:00:00+00', '2025-08-20 12:00:00+00', '2025-08-20 12:00:00+00'
),
(
  'NEWS_FilmTour0001',
  'ymD3MaEjEkbOmtxv8fye',
  'Ghana YMCA Concludes Cross-Country Filmmaking Training Tour',
  $c$Ghana YMCA has concluded a cross-country filmmaking training tour that took practical media education to young people beyond Accra.

At the Accra certificate ceremony, Executive Director Kwabena Nketia Addae thanked partners for staying the course and said the project gave young filmmakers hope and skills they can use for work and peacebuilding.

The tour is part of Ghana YMCA’s wider media and creative-industry work, including Resilience Africa and Digital Film School Africa.$c$,
  'A cross-country filmmaking tour equipped young storytellers in communities across Ghana, ending with a certificate ceremony in Accra.',
  'NEWS', true, NULL, NULL, true,
  '2026-05-12 12:00:00+00', '2026-05-12 12:00:00+00', '2026-05-12 12:00:00+00'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO news_media (id, news_id, url, media_type, "order") VALUES
('MEDIA_BritishCoun1', 'NEWS_BritishCoun1', 'https://ymcaghana.org/wp-content/uploads/2026/09/CS1A0584-1024x683.jpg', 'IMAGE', 0),
('MEDIA_YouthConf001', 'NEWS_YouthConf001', 'https://ymcaghana.org/wp-content/uploads/2026/09/DSF3343-1024x567.jpg', 'IMAGE', 0),
('MEDIA_CVJMInterns1', 'NEWS_CVJMInterns1', 'https://ymcaghana.org/wp-content/uploads/2026/08/WhatsApp-Image-2026-08-26-at-4.27.23-AM-2.jpeg', 'IMAGE', 0),
('MEDIA_ClinicDonat1', 'NEWS_ClinicDonat1', 'https://ymcaghana.org/wp-content/uploads/2025/09/558963013_1262604602573430_2295677114338709682_n-1024x536.jpg', 'IMAGE', 0),
('MEDIA_NuhuFamily01', 'NEWS_NuhuFamily01', 'https://ymcaghana.org/wp-content/uploads/2020/08/672674096_1420527290114493_5055487864127650862_n-1024x768.jpg', 'IMAGE', 0),
('MEDIA_FilmTour0001', 'NEWS_FilmTour0001', 'https://ymcaghana.org/wp-content/uploads/2026/05/702893555_1452629283570960_7183772618461304906_n-1-1024x766.jpg', 'IMAGE', 0)
ON CONFLICT (id) DO NOTHING;
