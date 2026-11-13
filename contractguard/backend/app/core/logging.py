import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


logger = logging.getLogger("contractguard")
setup_logging()


def log_llm_call(feature: str, tokens_in: int, tokens_out: int, latency_ms: int, contract_id: str = ""):
    """Logs LLM interaction stats strictly omitting contract raw text for privacy compliance."""
    logger.info(
        f"[LLM_CALL] feature={feature} contract_id={contract_id} "
        f"tokens_in={tokens_in} tokens_out={tokens_out} latency_ms={latency_ms}"
    )
