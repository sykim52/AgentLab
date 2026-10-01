from __future__ import annotations

from agent_lab.integrations.mcp.envelope import ToolStatus
from agent_lab.integrations.mcp.tools import invoke_tool, read_document, search_documents


def test_search_pto_ok():
    env = search_documents(query="PTO", correlation_id="t1")
    assert env.status == ToolStatus.OK
    assert env.items
    assert env.items[0]["id"] == "pol-pto-001"


def test_search_no_results():
    env = search_documents(query="zzzzqxrm nohitfoobar")
    assert env.status == ToolStatus.NO_RESULTS


def test_denied_not_collapsed_to_no_results():
    env = invoke_tool("admin_export", {}, correlation_id="t2")
    assert env.status == ToolStatus.DENIED
    assert env.status != ToolStatus.NO_RESULTS


def test_read_document():
    env = read_document(document_id="pol-sec-002")
    assert env.status == ToolStatus.OK
    assert "credentials" in env.items[0]["body"]
