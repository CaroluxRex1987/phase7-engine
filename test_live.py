from live_trading import live_trading_simulator

result = live_trading_simulator.run_once("AEROUSDT", "4h")

print()
print("=====================================")
print("Simulated order log saved to:")
print(result["log_path"])
print("=====================================")