from live_trading import get_live_trading_simulator

result = get_live_trading_simulator().run_once("AEROUSDT", "4h")

print()
print("=====================================")
print("Simulated order log saved to:")
print(result["log_path"])
print("=====================================")