-- 创建数据库
CREATE DATABASE IF NOT EXISTS vnpy DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE vnpy;

-- 创建 K 线数据表
CREATE TABLE IF NOT EXISTS dbbardata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(32) NOT NULL,
    datetime DATETIME(3) NOT NULL,
    interval VARCHAR(32) NOT NULL,
    volume DOUBLE,
    turnover DOUBLE,
    open_interest DOUBLE,
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    UNIQUE KEY idx_symbol_exchange_interval_datetime (symbol, exchange, interval, datetime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建 Tick 数据表
CREATE TABLE IF NOT EXISTS dbtickdata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(32) NOT NULL,
    datetime DATETIME(3) NOT NULL,
    name VARCHAR(32),
    volume DOUBLE,
    turnover DOUBLE,
    open_interest DOUBLE,
    last_price DOUBLE,
    last_volume DOUBLE,
    limit_up DOUBLE,
    limit_down DOUBLE,
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    pre_close DOUBLE,
    bid_price_1 DOUBLE,
    bid_price_2 DOUBLE,
    bid_price_3 DOUBLE,
    bid_price_4 DOUBLE,
    bid_price_5 DOUBLE,
    ask_price_1 DOUBLE,
    ask_price_2 DOUBLE,
    ask_price_3 DOUBLE,
    ask_price_4 DOUBLE,
    ask_price_5 DOUBLE,
    bid_volume_1 DOUBLE,
    bid_volume_2 DOUBLE,
    bid_volume_3 DOUBLE,
    bid_volume_4 DOUBLE,
    bid_volume_5 DOUBLE,
    ask_volume_1 DOUBLE,
    ask_volume_2 DOUBLE,
    ask_volume_3 DOUBLE,
    ask_volume_4 DOUBLE,
    ask_volume_5 DOUBLE,
    localtime DATETIME(3),
    UNIQUE KEY idx_symbol_exchange_datetime (symbol, exchange, datetime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建 K 线汇总表
CREATE TABLE IF NOT EXISTS dbbaroverview (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(32) NOT NULL,
    interval VARCHAR(32) NOT NULL,
    count INT,
    start DATETIME,
    end DATETIME,
    UNIQUE KEY idx_symbol_exchange_interval (symbol, exchange, interval)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建 Tick 汇总表
CREATE TABLE IF NOT EXISTS dbtickoverview (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(32) NOT NULL,
    count INT,
    start DATETIME,
    end DATETIME,
    UNIQUE KEY idx_symbol_exchange (symbol, exchange)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
