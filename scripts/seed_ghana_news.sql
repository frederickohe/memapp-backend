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
('MEDIA_ImpactAward1', 'NEWS_ImpactAward1', 'https://ymcaghana.org/wp-content/uploads/2026/08/ChatGPT-Image-Aug-6-2026-04_43_21-PM-1024x768.png', 'IMAGE', 0),
('MEDIA_PresidentElc', 'NEWS_PresidentElc', 'https://ymcaghana.org/wp-content/uploads/2026/08/WhatsApp-Image-2026-08-25-at-8.37.14-AM-1024x768.jpeg', 'IMAGE', 0),
('MEDIA_SmartGirl001', 'NEWS_SmartGirl001', 'https://ymcaghana.org/wp-content/uploads/2026/06/smart.jpg', 'IMAGE', 0),
('MEDIA_YouthJustic1', 'NEWS_YouthJustic1', 'https://ymcaghana.org/wp-content/uploads/2026/04/Youth-Justice-iii.jpg', 'IMAGE', 0),
('MEDIA_GreenIdeas01', 'NEWS_GreenIdeas01', 'https://ymcaghana.org/wp-content/uploads/2026/06/green.jpg', 'IMAGE', 0),
('MEDIA_Resilience01', 'NEWS_Resilience01', 'https://ymcaghana.org/wp-content/uploads/2026/06/Resilience-Africa-cover2.jpg', 'IMAGE', 0),
('MEDIA_FilmSchool01', 'NEWS_FilmSchool01', 'https://ymcaghana.org/wp-content/uploads/2026/05/dfs-1024x683.jpg', 'IMAGE', 0),
('MEDIA_EarthDay0001', 'NEWS_EarthDay0001', 'https://ymcaghana.org/wp-content/uploads/2025/07/mother.jpg', 'IMAGE', 0)
ON CONFLICT (id) DO NOTHING;
