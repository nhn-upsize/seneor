CREATE TABLE IF NOT EXISTS dart_st_publisher_map (
    corp_code       VARCHAR(20) NOT NULL REFERENCES dart_company(corp_code),
    publisher_name  VARCHAR(200) NOT NULL,
    note            VARCHAR(200),
    PRIMARY KEY (corp_code, publisher_name)
);

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
('01210190', 'mobirix', NULL),
('01210190', 'MOBIRIX', NULL),
-- 엔씨소프트
('00261443', 'NCSOFT', NULL),
('00261443', 'NC Corporation', NULL),
-- 엠게임
('00397058', 'Mgame', NULL),
('00397058', 'MGAME Corp.', NULL),
-- 웹젠
('00405320', 'Webzen Inc.', NULL),
('00405320', 'WEBZEN INC.', NULL),
-- 위메이드
('00444329', 'Wemade Co., Ltd', NULL),
('00444329', 'Wemade Co., Ltd.', NULL),
-- 위메이드맥스
('00643656', 'Wemade Max Co., Ltd.', NULL),
-- 위메이드플레이
('00815767', 'Wemade Play Co.,Ltd.', NULL),
('00815767', 'Wemade Connect', 'formerly Wemade Connect'),
('00815767', 'Wemade Connect Co., Ltd.', 'formerly Wemade Connect'),
-- 조이시티
('00397252', 'JOYCITY Corp', NULL),
('00397252', 'JOYCITY Corp.', NULL),
-- 카카오게임즈
('01137383', 'Kakao Games Corp.', NULL),
-- 컴투스
('00476498', 'Com2uS', NULL),
('00476498', 'Com2uS Corp.', NULL),
('00476498', 'Com2uS Japan Inc.', NULL),
-- 컴투스홀딩스
('00535746', 'Com2uS Holdings', NULL),
-- 크래프톤
('00760971', 'KRAFTON Inc', NULL),
('00760971', 'KRAFTON, Inc.', NULL),
-- 펄어비스
('01152470', 'PEARL ABYSS', NULL),
('01152470', 'Pearl Abyss Corp.', NULL),
-- 플레이위드
('00138367', 'PLAYWITH Inc', NULL),
('00138367', 'PlaywithKorea Inc.', NULL),
-- 한빛소프트
('00348292', 'HanbitSoft Inc', NULL),
('00348292', 'hanbitsoft inc.', NULL)
ON CONFLICT DO NOTHING;
