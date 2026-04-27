INSERT INTO dart_st_publisher_map (corp_code, publisher_name, note) VALUES
-- NHN
('00983271', 'NHN Corp.', NULL),
-- 골프존
('01067516', 'GOLFZON Corp.', NULL),
-- 네오위즈
('00628860', 'NEOWIZ', NULL),
('00628860', 'NEOWIZ corp', NULL),
-- 넥슨게임즈 -> NEXON
('01096341', 'NEXON Co., Ltd.', 'nexon subsidiary'),
('01096341', 'NEXON Company', 'nexon subsidiary'),
-- 넥슨지티 -> NEXON
('00266943', 'NEXON Co., Ltd.', 'nexon subsidiary'),
('00266943', 'NEXON Company', 'nexon subsidiary'),
-- 넵튠
('01067808', 'Neptune Company', NULL),
('01067808', 'Neptune Corp.', NULL),
-- 넷마블
('00904672', 'Netmarble', NULL),
('00904672', 'Netmarble Corporation', NULL),
-- 더블유게임즈
('01010110', 'DoubleUGames', NULL),
('01010110', 'DoubleUGames Co., Ltd.', NULL),
-- 데브시스터즈
('01008762', 'Devsisters', NULL),
('01008762', 'Devsisters Corporation', NULL),
-- 드래곤플라이
('00230036', 'DRAGONFLY GF CO., LTD.', NULL),
-- 모비릭스
('00550498', 'mobirix', NULL),
('00550498', 'MOBIRIX', NULL),
-- 엔씨소프트
('00261443', 'NCSOFT', NULL),
('00261443', 'NC Corporation', NULL),
-- 엠게임
('00316538', 'Mgame', NULL),
('00316538', 'MGAME Corp.', NULL),
-- 웹젠
('00550447', 'Webzen Inc.', NULL),
('00550447', 'WEBZEN INC.', NULL),
-- 위메이드
('00429653', 'Wemade Co., Ltd', NULL),
('00429653', 'Wemade Co., Ltd.', NULL),
-- 위메이드맥스
('01065753', 'Wemade Max Co., Ltd.', NULL),
-- 위메이드플레이
('00856842', 'Wemade Play Co.,Ltd.', NULL),
('00856842', 'Wemade Connect', 'formerly Wemade Connect'),
('00856842', 'Wemade Connect Co., Ltd.', 'formerly Wemade Connect'),
-- 조이시티
('00350793', 'JOYCITY Corp', NULL),
('00350793', 'JOYCITY Corp.', NULL),
-- 카카오게임즈
('01051415', 'Kakao Games Corp.', NULL),
-- 컴투스
('00508063', 'Com2uS', NULL),
('00508063', 'Com2uS Corp.', NULL),
('00508063', 'Com2uS Japan Inc.', NULL),
-- 컴투스홀딩스
('00432423', 'Com2uS Holdings', NULL),
-- 크래프톤
('01126498', 'KRAFTON Inc', NULL),
('01126498', 'KRAFTON, Inc.', NULL),
-- 펄어비스
('01033713', 'PEARL ABYSS', NULL),
('01033713', 'Pearl Abyss Corp.', NULL),
-- 플레이위드
('00649891', 'PLAYWITH Inc', NULL),
('00649891', 'PlaywithKorea Inc.', NULL),
-- 한빛소프트
('00352076', 'HanbitSoft Inc', NULL),
('00352076', 'hanbitsoft inc.', NULL)
ON CONFLICT DO NOTHING;
