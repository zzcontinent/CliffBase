/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50724
 Source Host           : localhost:3306
 Source Schema         : metadata

 Target Server Type    : MySQL
 Target Server Version : 50724
 File Encoding         : 65001

 Date: 24/12/2018 15:37:04
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for db_config
-- ----------------------------
DROP TABLE IF EXISTS `db_config`;
CREATE TABLE `db_config`  (
  `db_config_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `is_enabled` int(4) NULL DEFAULT 1 COMMENT '是否有效',
  `is_display` tinyint(255) NULL DEFAULT 0 COMMENT '是否展示: 1展示 0不展示',
  `env` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `conn_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `conn_type` int(4) NULL DEFAULT NULL COMMENT '连接类型0:数据库连接,1:ssh连接',
  `user` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `passwd` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `host` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `port` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `db_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `ssh_sts` tinyint(1) NULL DEFAULT 0 COMMENT '0:不需要ssh, 1:需要ssh',
  `ssh_sk` int(4) NULL DEFAULT NULL COMMENT 'ssh对应的配置db_config_id',
  `charset` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'utf8' COMMENT '数据库编码，如utf8',
  `created_tm` datetime(6) NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'CURRENT_TIMESTAMP(6)',
  `created_by` bigint(20) NULL DEFAULT NULL,
  `updated_tm` datetime(6) NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(6),
  `updated_by` bigint(20) NULL DEFAULT NULL,
  PRIMARY KEY (`db_config_id`) USING BTREE,
  UNIQUE INDEX `conn_name_unique`(`conn_name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 32 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of db_config
-- ----------------------------
INSERT INTO `db_config` VALUES (2, 1, 1, 'local', 'local_ods_jff', 0, 'root', 'b2be9c5d296a1a52', 'localhost', '3306', 'ods_jff', 0, NULL, 'utf8', '2018-09-05 15:19:50.657570', NULL, '2018-11-02 13:42:30.168180', NULL);
INSERT INTO `db_config` VALUES (19, 1, 1, 'local', 'local_stg_ods_jff', 0, 'root', 'b2be9c5d296a1a52', 'localhost', '3306', 'stg_ods_jff', 0, NULL, 'utf8', '2018-09-06 15:48:53.186344', NULL, '2018-11-02 13:42:35.266059', NULL);
INSERT INTO `db_config` VALUES (20, 1, 0, 'local', 'local_information', 0, 'root', 'b2be9c5d296a1a52', 'localhost', '3306', 'information_schema', 0, NULL, 'utf8', '2018-09-06 15:58:58.312449', NULL, '2018-11-02 13:42:36.123685', NULL);
INSERT INTO `db_config` VALUES (22, 1, 1, 'local', 'local_metadata', 0, 'root', 'b2be9c5d296a1a52', 'localhost', '3306', 'metadata', 0, NULL, 'utf8', '2018-09-06 14:37:52.348277', NULL, '2018-11-02 13:42:37.566229', NULL);

SET FOREIGN_KEY_CHECKS = 1;
