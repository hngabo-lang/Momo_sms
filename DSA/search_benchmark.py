import json
import time

def linear_search(transactions_list, target_id):
    for tx in transactions_list:
        if tx.get("id") == target_id:
            return tx
    return None

def dict_lookup(transactions_dict, target_id):
    return transactions_dict.get(target_id)

def run_benchmark():
    with open("DSA/transactions.json", "r", encoding="utf-8") as f:
        transactions_list = json.load(f)
    
    transactions_dict = {tx["id"]: tx for tx in transactions_list}
    
    sample_ids = [tx["id"] for tx in transactions_list[:20]]
    if len(transactions_list) >= 1000:
        sample_ids += [transactions_list[i]["id"] for i in range(100, 1000, 50)]
    
    print(f"Loaded {len(transactions_list)} records for benchmarking.\n")
    print(f"{'Target ID':<12} | {'Linear Search (s)':<20} | {'Dict Lookup (s)':<20} | {'Speedup Factor':<15}")
    print("-" * 75)
    
    total_linear_time = 0
    total_dict_time = 0
    iterations = 1000
    
    for target_id in sample_ids[:20]:
        start = time.perf_counter()
        for _ in range(iterations):
            linear_search(transactions_list, target_id)
        linear_time = (time.perf_counter() - start) / iterations
        total_linear_time += linear_time

        start = time.perf_counter()
        for _ in range(iterations):
            dict_lookup(transactions_dict, target_id)
        dict_time = (time.perf_counter() - start) / iterations
        total_dict_time += dict_time

        speedup = linear_time / dict_time if dict_time > 0 else 0
        print(f"{target_id:<12} | {linear_time:<20.8f} | {dict_time:<20.8f} | {speedup:<15.2f}x")

    avg_linear = total_linear_time / 20
    avg_dict = total_dict_time / 20
    print("-" * 75)
    print(f"AVERAGE      | {avg_linear:<20.8f} | {avg_dict:<20.8f} | {(avg_linear/avg_dict):<15.2f}x faster")

if __name__ == "__main__":
    run_benchmark()