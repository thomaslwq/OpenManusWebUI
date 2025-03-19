"""
ツール用の設定管理モジュール
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# ロガー設定
logger = logging.getLogger(__name__)

# 設定ファイルのパス
CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config"
TOOLS_CONFIG_FILE = CONFIG_DIR / "tools_config.json"

# デフォルト設定
DEFAULT_CONFIG = {
    "github": {
        "access_token": "",
        "username": "",
        "repositories": []
    },
    "web_search": {
        "api_key": ""
    }
}


def ensure_config_exists():
    """設定ファイルの存在を確認し、なければデフォルト設定で作成"""
    CONFIG_DIR.mkdir(exist_ok=True)
    
    if not TOOLS_CONFIG_FILE.exists():
        with open(TOOLS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        logger.info(f"デフォルト設定ファイルを作成しました: {TOOLS_CONFIG_FILE}")


def load_config() -> Dict[str, Any]:
    """設定をロード"""
    ensure_config_exists()
    
    try:
        with open(TOOLS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 追加: 設定が読み込めたかログ出力（機密情報はマスク）
        log_config = {}
        for tool, tool_config in config.items():
            log_config[tool] = {}
            for key, value in tool_config.items():
                if key in ["api_key", "access_token", "secret", "password", "key"]:
                    log_config[tool][key] = "********" if value else ""
                else:
                    log_config[tool][key] = value
        
        logger.info(f"設定ファイルを読み込みました: {json.dumps(log_config)}")
        return config
    except Exception as e:
        logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]):
    """設定を保存"""
    ensure_config_exists()
    
    try:
        with open(TOOLS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info("設定ファイルを保存しました")
    except Exception as e:
        logger.error(f"設定ファイルの保存に失敗しました: {e}")


def get_tool_config(tool_name: str) -> Dict[str, Any]:
    """特定のツールの設定を取得"""
    config = load_config()
    tool_config = config.get(tool_name, {})
    
    # ログ出力（機密情報はマスク）
    log_config = {}
    for key, value in tool_config.items():
        if key in ["api_key", "access_token", "secret", "password", "key"]:
            log_config[key] = "********" if value else ""
        else:
            log_config[key] = value
    
    logger.debug(f"ツール '{tool_name}' の設定を取得: {json.dumps(log_config)}")
    return tool_config


def update_tool_config(tool_name: str, tool_config: Dict[str, Any]):
    """特定のツールの設定を更新"""
    config = load_config()
    config[tool_name] = tool_config
    
    # ログ出力（機密情報はマスク）
    log_config = {}
    for key, value in tool_config.items():
        if key in ["api_key", "access_token", "secret", "password", "key"]:
            log_config[key] = "設定あり" if value else ""
        else:
            log_config[key] = value
    
    logger.info(f"ツール '{tool_name}' の設定を更新: {json.dumps(log_config)}")
    save_config(config)


def get_env_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """環境変数から設定を取得（設定ファイルの値を上書きする場合などに使用）"""
    value = os.environ.get(key, default)
    
    # 環境変数が設定されていればログ出力（機密情報はマスク）
    if value is not None and value != default:
        if any(secret in key.lower() for secret in ["token", "key", "secret", "password"]):
            logger.info(f"環境変数 '{key}' が設定されています")
        else:
            logger.info(f"環境変数 '{key}' = '{value}' が設定されています")
    
    return value


# 環境変数からの設定をチェック（セキュリティのため、APIキーなどを環境変数に保存することを推奨）
def check_env_settings():
    """環境変数による設定の上書き確認"""
    config = load_config()
    updated = False
    
    # GitHub設定の確認
    github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if github_token and config.get("github", {}).get("access_token") != github_token:
        if "github" not in config:
            config["github"] = {}
        config["github"]["access_token"] = github_token
        logger.info("環境変数 GITHUB_PERSONAL_ACCESS_TOKEN から設定を更新しました")
        updated = True
    
    github_username = os.environ.get("GITHUB_USERNAME")
    if github_username and config.get("github", {}).get("username") != github_username:
        if "github" not in config:
            config["github"] = {}
        config["github"]["username"] = github_username
        logger.info(f"環境変数 GITHUB_USERNAME から設定を更新しました: {github_username}")
        updated = True
    
    # Web検索設定の確認
    brave_search_api_key = os.environ.get("BRAVE_API_KEY")
    if brave_search_api_key and config.get("web_search", {}).get("api_key") != brave_search_api_key:
        if "web_search" not in config:
            config["web_search"] = {}
        config["web_search"]["api_key"] = brave_search_api_key
        logger.info("環境変数 BRAVE_API_KEY から設定を更新しました")
        updated = True
    
    # 更新があれば保存
    if updated:
        logger.info("環境変数から設定を更新しました")
        save_config(config)


# アプリケーション起動時に環境変数を確認
check_env_settings()
