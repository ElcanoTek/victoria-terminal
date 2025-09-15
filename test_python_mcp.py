import asyncio

async def main():
    # Test package installation
    install_result = await mcp.python_install_package(package="requests")
    print(f"Install result: {install_result}")
    assert install_result["success"], "Failed to install package"

    # Test code execution
    code_to_execute = "import requests; print(requests.__version__)"
    execution_result = await mcp.python_execute(code=code_to_execute)
    print(f"Execution result: {execution_result}")
    assert execution_result["success"], "Failed to execute code"

    # Test package uninstallation
    uninstall_result = await mcp.python_uninstall_package(package="requests")
    print(f"Uninstall result: {uninstall_result}")
    assert uninstall_result["success"], "Failed to uninstall package"

if __name__ == "__main__":
    asyncio.run(main())


