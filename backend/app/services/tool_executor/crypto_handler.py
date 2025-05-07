import logging
import ccxt.async_support as ccxt  # 使用 ccxt 的异步版本
from typing import List, Dict, Any
from .base_tool_handler import BaseToolHandler

logger = logging.getLogger(__name__)

# TODO: 实现正确的 API 密钥处理和基于用户配置的交易所实例化
# 目前，如果适用，使用占位符或公共方法
async def get_exchange_instance(exchange_name: str = 'binance', api_key: str = None, secret: str = None):
    """占位符函数，用于获取经过身份验证或未经身份验证的 ccxt 交易所实例。"""
    exchange_class = getattr(ccxt, exchange_name, None)
    if not exchange_class:
        raise ValueError(f"在 ccxt 中未找到交易所 '{exchange_name}'。")

    config = {}
    if api_key and secret:
        config['apiKey'] = api_key
        config['secret'] = secret
        # 如果需要，添加其他潜在的认证参数，如密码

    # 默认启用速率限制
    config['enableRateLimit'] = True

    exchange = exchange_class(config)
    # TODO: 如果需要，考虑显式加载市场：await exchange.load_markets()
    return exchange


class CryptoToolHandler(BaseToolHandler):
    """处理加密货币市场的工具执行。"""

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        为加密市场执行特定的工具。

        Args:
            tool_name: 要执行的工具名称。
            parameters: 工具的参数字典。
                        预期的键可能包括 'exchange_config_id' 或类似内容以获取凭证，
                        或 'exchange_name' 用于公共数据。

        Returns:
            包含工具执行结果的字典。
            格式: {"status": "success" | "error", "data": ..., "message": ...}
        """
        logger.info(f"执行加密工具: {tool_name}，参数: {parameters}")

        # --- 获取交易所实例 (占位符) ---
        # 这需要替换为基于参数（例如 exchange_config_id）获取用户配置并解密凭证的逻辑。
        exchange_name = parameters.get("exchange_name", "binance") # 暂时默认为 binance
        # api_key = 从数据库解密的 api_key
        # secret = 从数据库解密的 secret
        exchange = None
        try:
            # 对公共数据工具（如 get_historical_klines）使用未经身份验证的实例
            exchange = await get_exchange_instance(exchange_name) # api_key, secret)

            if tool_name == "get_historical_klines":
                return await self._get_historical_klines(exchange, parameters)
            elif tool_name == "get_current_ticker_info":
                return await self._get_current_ticker_info(exchange, parameters)
            elif tool_name == "create_order":
                # TODO: 实现 create_order (需要认证)
                logger.warning("CryptoToolHandler: create_order 尚未实现。")
                return {"status": "error", "data": None, "message": f"工具 '{tool_name}' 尚未为加密市场实现。"}
            # 在此处添加其他加密货币特定的工具处理程序
            else:
                logger.error(f"为加密市场请求了未知工具: {tool_name}")
                return {"status": "error", "data": None, "message": f"未知工具: {tool_name}"}

        except Exception as e:
            logger.error(f"执行加密工具 '{tool_name}' 时出错: {e}", exc_info=True)
            return {"status": "error", "data": None, "message": f"执行工具 '{tool_name}' 时出错: {str(e)}"}
        finally:
            if exchange:
                try:
                    await exchange.close() # 关闭 ccxt 连接
                except Exception as close_exc:
                    logger.error(f"关闭交易所连接时出错: {close_exc}", exc_info=True)

    async def _get_historical_klines(self, exchange: ccxt.Exchange, parameters: dict) -> Dict[str, Any]:
        """获取历史 K 线 (OHLCV) 数据。"""
        try:
            symbol = parameters.get("symbol")
            interval = parameters.get("interval", "1h")
            limit = parameters.get("limit", 100)
            limit = int(limit) # 确保 limit 是整数
            # since = parameters.get("since") # 可选：开始时间的毫秒时间戳

            if not symbol:
                return {"status": "error", "data": None, "message": "缺少必需参数: symbol"}

            # 如果可能，验证时间间隔（ccxt 通常会处理，但基本检查是好的）
            if interval not in exchange.timeframes:
                 logger.warning(f"时间间隔 '{interval}' 可能不受 {exchange.id} 支持。支持的: {list(exchange.timeframes.keys())}")
                 # 仍然继续，ccxt 可能会映射它或稍后抛出错误

            logger.info(f"正在获取 {symbol} 的 K 线数据，时间间隔 {interval}，数量 {limit}")

            # 使用 ccxt 获取 OHLCV 数据
            # ccxt fetch_ohlcv 返回: [[timestamp, open, high, low, close, volume], ...]
            ohlcv_data = await exchange.fetch_ohlcv(symbol, timeframe=interval, limit=limit) #, since=since)

            if not ohlcv_data:
                return {"status": "success", "data": [], "message": f"未返回 {symbol} {interval} 的 K 线数据。"}

            # 按要求格式化数据
            formatted_data = [
                {
                    "timestamp": int(kline[0]), # 确保时间戳是整数
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5])
                }
                for kline in ohlcv_data
            ]

            return {"status": "success", "data": formatted_data, "message": f"成功获取 {len(formatted_data)} 条 {symbol} {interval} 的 K 线数据。"}

        except ccxt.NetworkError as e:
            logger.error(f"获取 {parameters.get('symbol')} 的 K 线数据时发生 CCXT 网络错误: {e}", exc_info=True)
            return {"status": "error", "data": None, "message": f"连接到 {exchange.id} 时发生网络错误: {e}"}
        except ccxt.ExchangeError as e:
            logger.error(f"获取 {parameters.get('symbol')} 的 K 线数据时发生 CCXT 交易所错误: {e}", exc_info=True)
            return {"status": "error", "data": None, "message": f"来自 {exchange.id} 的交易所错误: {e}"}
        except Exception as e:
            logger.error(f"获取 {parameters.get('symbol')} 的 K 线数据时发生意外错误: {e}", exc_info=True)
            return {"status": "error", "data": None, "message": f"发生意外错误: {str(e)}"}

    async def _get_current_ticker_info(self, exchange: ccxt.Exchange, parameters: dict) -> Dict[str, Any]:
        """获取一个或多个指定交易标的的最新行情摘要信息。"""
        try:
            symbols = parameters.get("symbols")
            if not symbols:
                return {"status": "error", "data": None, "message": "Missing required parameter: symbols"}

            # Ensure symbols is a list
            if isinstance(symbols, str):
                symbols = [symbols]
            elif not isinstance(symbols, list):
                 return {"status": "error", "data": None, "message": "Parameter 'symbols' must be a string or a list of strings."}

            logger.info(f"Fetching ticker info for {symbols}")

            # Fetch ticker data using ccxt's fetch_tickers method
            # fetch_tickers usually returns a dictionary where keys are symbols
            tickers_data = await exchange.fetch_tickers(symbols)

            if not tickers_data:
                return {"status": "success", "data": {}, "message": f"No ticker data returned for symbols: {symbols}."}

            # Format data (ccxt ticker structure can vary, we extract common fields)
            # Refer to technical_specs.md Section 6.1 for desired output format
            formatted_data = {}
            for symbol, ticker in tickers_data.items():
                formatted_data[symbol] = {
                    "symbol": ticker.get("symbol"),
                    "timestamp": ticker.get("timestamp"), # ms Unix timestamp of when the ticker was generated
                    "last": ticker.get("last"),           # Last traded price
                    "high": ticker.get("high"),           # 24h high price
                    "low": ticker.get("low"),            # 24h low price
                    "bid": ticker.get("bid"),             # Current best bid (buy) price
                    "ask": ticker.get("ask"),             # Current best ask (sell) price
                    "change": ticker.get("change"),       # Absolute change in price (usually 24h)
                    "percentage": ticker.get("percentage"), # Percentage change in price (usually 24h)
                    "average": ticker.get("average"),     # Average price (usually 24h)
                    "baseVolume": ticker.get("baseVolume"), # Volume in base currency (e.g., BTC for BTC/USDT) traded in the last 24 hours
                    "quoteVolume": ticker.get("quoteVolume") # Volume in quote currency (e.g., USDT for BTC/USDT) traded in the last 24 hours
                    # Add other relevant fields from ticker['info'] if needed, be mindful of inconsistencies
                }

            return {"status": "success", "data": formatted_data, "message": f"Successfully fetched ticker info for {list(formatted_data.keys())}."}

        except ccxt.NetworkError as e:
            logger.error(f"CCXT Network Error fetching tickers for {parameters.get('symbols')}: {e}", exc_info=True)
            return {"status": "error", "data": None, "message": f"Network error connecting to {exchange.id}: {e}"}
        except ccxt.ExchangeError as e:
            logger.error(f"CCXT Exchange Error fetching tickers for {parameters.get('symbols')}: {e}", exc_info=True)
            return {"status": "error", "data": None, "message": f"Exchange error from {exchange.id}: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error fetching tickers for {parameters.get('symbols')}: {e}", exc_info=True)
            return {"status": "error", "data": None, "message": f"An unexpected error occurred: {str(e)}"}

# 提示: 需要安装 ccxt 库: pip install ccxt