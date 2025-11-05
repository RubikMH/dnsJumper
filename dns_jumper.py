import sys
import os
import subprocess
import platform
import time
import re
import json

# --- Configuration ---

# Load DNS servers from dnsList.json
def load_dns_servers():
    """Load DNS servers from dnsList.json file."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file = os.path.join(script_dir, "dnsList.json")
        with open(json_file, 'r') as f:
            data = json.load(f)
        return data["list"]  # Return full list with id, ip, and company
    except FileNotFoundError:
        print("Error: dnsList.json not found in the script directory.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: dnsList.json is not valid JSON.")
        sys.exit(1)

DNS_SERVERS = load_dns_servers()

# Number of pings per DNS server for performance testing
PINGS_PER_SERVER = 15

# Number of top DNS servers to recommend
TOP_DNS_COUNT = 4

# --- OS-Specific Functions ---

def get_active_interface_macos():
    """Get the primary network service on macOS (e.g., 'Wi-Fi')."""
    try:
        cmd = "scutil <<< 'show State:/Network/Global/IPv4' | awk -F': ' '/PrimaryService/ {print $2}'"
        service_guid = subprocess.check_output(cmd, shell=True, text=True, executable='/bin/bash').strip()
        if service_guid:
            cmd = f"scutil <<< 'show Setup:/Network/Service/{service_guid}' | awk -F': ' '/UserDefinedName/ {{print $2}}'"
            return subprocess.check_output(cmd, shell=True, text=True, executable='/bin/bash').strip()
    except Exception:
        services = subprocess.check_output(["networksetup", "-listallnetworkservices"], text=True).strip().split('\n')
        for service in services[1:]:
            if "wi-fi" in service.lower() or "ethernet" in service.lower():
                return service
    return None

def set_dns_macos(interface, dns_ips):
    """Set DNS servers on macOS. dns_ips is a list of IP addresses."""
    dns_list = " ".join(dns_ips)
    log(f"Setting DNS for '{interface}' to {dns_list}")
    subprocess.run(["networksetup", "-setdnsservers", interface] + dns_ips, check=True)
    clear_dns_cache()

def get_active_interface_linux():
    """Get the primary network interface on Linux using nmcli."""
    try:
        cmd = "nmcli -t -f DEVICE,STATE d | grep ':connected' | cut -d':' -f1 | head -n 1"
        device = subprocess.check_output(cmd, shell=True, text=True).strip()
        if device:
             cmd = f"nmcli -t -f NAME,DEVICE c show --active | grep '{device}' | cut -d':' -f1 | head -n 1"
             return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return None

def set_dns_linux(interface_name, dns_ips):
    """Set DNS servers on Linux using nmcli. dns_ips is a list of IP addresses."""
    dns_str = " ".join(dns_ips)
    log(f"Setting DNS for '{interface_name}' to {dns_str}")
    subprocess.run(["nmcli", "con", "mod", interface_name, "ipv4.dns", dns_str], check=True)
    subprocess.run(["nmcli", "con", "up", interface_name], check=True)
    clear_dns_cache()

def get_active_interface_windows():
    """Get the primary network interface on Windows."""
    try:
        cmd = "powershell -Command \"Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null -and $_.NetAdapter.Status -eq 'Up' } | Select-Object -ExpandProperty InterfaceAlias\""
        return subprocess.check_output(cmd, shell=True, text=True).strip().split('\n')[0]
    except Exception:
        return None

def set_dns_windows(interface, dns_ips):
    """Set DNS servers on Windows. dns_ips is a list of IP addresses."""
    dns_str = " ".join(dns_ips)
    log(f"Setting DNS for '{interface}' to {dns_str}")
    subprocess.run(f'netsh interface ipv4 set dnsservers name="{interface}" static {dns_ips[0]} primary', shell=True, check=True)
    for idx, dns_ip in enumerate(dns_ips[1:], start=2):
        subprocess.run(f'netsh interface ipv4 add dnsservers name="{interface}" {dns_ip} index={idx}', shell=True, check=True)
    clear_dns_cache()

def clear_dns_cache():
    """Clear DNS cache based on the operating system."""
    os_name = platform.system()
    
    try:
        log("Clearing DNS cache...")
        
        if os_name == "Darwin":  # macOS
            subprocess.run(["dscacheutil", "-flushcache"], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["killall", "-HUP", "mDNSResponder"], check=True, stderr=subprocess.DEVNULL)
            log("DNS cache cleared successfully.")
            
        elif os_name == "Linux":
            # Try different methods for different Linux distributions
            try:
                # systemd-resolved (Ubuntu 18.04+, Debian 10+)
                subprocess.run(["resolvectl", "flush-caches"], check=True, stderr=subprocess.DEVNULL)
                log("DNS cache cleared successfully.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(["systemd-resolve", "--flush-caches"], check=True, stderr=subprocess.DEVNULL)
                    log("DNS cache cleared successfully.")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        # nscd
                        subprocess.run(["nscd", "-i", "hosts"], check=True, stderr=subprocess.DEVNULL)
                        log("DNS cache cleared successfully.")
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        log("Note: No DNS cache service found on this Linux system.")
            
        elif os_name == "Windows":
            subprocess.run(["ipconfig", "/flushdns"], check=True, stderr=subprocess.DEVNULL)
            log("DNS cache cleared successfully.")
            
    except Exception as e:
        log(f"Warning: Could not clear DNS cache: {e}")

def ping_server(ip_address):
    """Pings a server to measure latency and returns the time in ms as a float."""
    try:
        os_name = platform.system()
        # Build the ping command based on the OS
        if os_name == "Windows":
            command = ["ping", "-n", "1", "-w", "1000", ip_address]
        elif os_name == "Darwin": # macOS
            command = ["ping", "-c", "1", "-W", "1000", ip_address]
        else: # Linux
            command = ["ping", "-c", "1", "-W", "1", ip_address]

        output = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL)

        # Parse the output to find the latency
        if os_name == "Windows":
            match = re.search(r"Average = (\d+)", output)
            if match:
                return float(match.group(1))
        else: # macOS & Linux
            match = re.search(r"time=([\d.]+)", output)
            if match:
                return float(match.group(1))

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return None

def test_dns_performance(ip_address, num_pings=5):
    """Test a DNS server by pinging it multiple times and return stats."""
    log(f"Testing {ip_address}...")
    latencies = []
    
    for i in range(num_pings):
        latency = ping_server(ip_address)
        if latency is not None:
            log(f"  Ping {i+1}/{num_pings} to {ip_address}: {latency:.2f} ms")
            latencies.append(latency)
        else:
            log(f"  Ping {i+1}/{num_pings} to {ip_address}: Timeout or Unreachable")
        time.sleep(0.5)  # Small delay between pings

    if latencies:
        min_lat = min(latencies)
        max_lat = max(latencies)
        avg_lat = sum(latencies) / len(latencies)
        log(f"Summary for {ip_address}: Min={min_lat:.2f}ms, Max={max_lat:.2f}ms, Avg={avg_lat:.2f}ms")
        return {
            "ip": ip_address,
            "min": min_lat,
            "max": max_lat,
            "avg": avg_lat,
            "successful_pings": len(latencies)
        }
    else:
        log(f"Failed to ping {ip_address}")
        return {
            "ip": ip_address,
            "min": float('inf'),
            "max": 0,
            "avg": float('inf'),
            "successful_pings": 0
        }

# --- Main Logic ---

def log(message):
    """Prints a message with a timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_privileges():
    """Check for root/admin privileges and exit if not found."""
    is_admin = False
    try:
        if platform.system() == "Windows":
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        else: # macOS & Linux
            is_admin = os.geteuid() == 0
    except Exception:
        pass # Could fail in some environments

    if not is_admin:
        log("Error: This script requires administrative/root privileges.")
        log("Please run it with 'sudo' (macOS/Linux) or as an Administrator (Windows).")
        sys.exit(1)

def main():
    """Main function to test all DNS servers and recommend the best ones."""
    check_privileges()
    os_name = platform.system()

    if os_name == "Darwin":
        log("macOS detected.")
        get_interface, set_dns = get_active_interface_macos, set_dns_macos
    elif os_name == "Linux":
        log("Linux detected. This script requires NetworkManager (nmcli).")
        get_interface, set_dns = get_active_interface_linux, set_dns_linux
    elif os_name == "Windows":
        log("Windows detected.")
        get_interface, set_dns = get_active_interface_windows, set_dns_windows
    else:
        log(f"Unsupported OS: {os_name}")
        sys.exit(1)

    interface = get_interface()
    if not interface:
        log("Error: Could not determine the active network interface.")
        sys.exit(1)

    log(f"Active network interface: '{interface}'")
    
    # Clear DNS cache before testing
    clear_dns_cache()
    
    log(f"Starting performance tests on {len(DNS_SERVERS)} DNS servers...")
    log("This may take a few minutes...")

    # Test all DNS servers
    results = []
    for idx, dns_entry in enumerate(DNS_SERVERS, 1):
        try:
            dns_ip = dns_entry["ip"]
            dns_company = dns_entry["company"]
            log(f"\n[{idx}/{len(DNS_SERVERS)}] Testing DNS server: {dns_ip} ({dns_company})")
            result = test_dns_performance(dns_ip, PINGS_PER_SERVER)
            result["company"] = dns_company  # Add company name to result
            results.append(result)
        except Exception as e:
            log(f"Error testing {dns_entry.get('ip', 'unknown')}: {e}")
            continue

    # Sort results by average latency (lower is better)
    results_sorted = sorted([r for r in results if r["successful_pings"] > 0], key=lambda x: x["avg"])

    print("\n" + "="*60)
    log(f"PERFORMANCE TEST RESULTS ({len(results_sorted)}/{len(DNS_SERVERS)} servers responded)")
    print("="*60)
    
    for idx, result in enumerate(results_sorted, 1):
        company = result.get('company', 'Unknown')
        log(f"{idx}. {result['ip']:18} ({company:30}) | Avg: {result['avg']:7.2f}ms | Min: {result['min']:7.2f}ms | Max: {result['max']:7.2f}ms")

    # Recommend top 4 DNS servers
    top_dns = results_sorted[:TOP_DNS_COUNT]
    
    print("\n" + "="*60)
    log(f"TOP {TOP_DNS_COUNT} RECOMMENDED DNS SERVERS:")
    print("="*60)
    for idx, result in enumerate(top_dns, 1):
        company = result.get('company', 'Unknown')
        log(f"{idx}. {result['ip']:18} ({company:30}) | Avg latency: {result['avg']:.2f}ms")

    # Ask for user confirmation
    print("-"*60)
    response = input("[y/n] Set your DNS to these recommended servers? ").strip().lower()

    if response == "y":
        try:
            dns_ips_to_set = [result["ip"] for result in top_dns]
            log(f"Setting DNS servers to: {', '.join(dns_ips_to_set)}")
            set_dns(interface, dns_ips_to_set)
            log("DNS settings updated successfully!")
        except Exception as e:
            log(f"Error setting DNS: {e}")
            sys.exit(1)
    else:
        log("DNS settings were not changed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
