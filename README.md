# DNS Jumper 🚀

A cross-platform DNS performance testing and optimization tool that automatically finds and configures the fastest DNS servers for your system.

## ✨ Features

- 🔍 **Performance Testing**: Tests 50+ public DNS servers and measures their actual latency
- 📊 **Detailed Statistics**: Shows min, max, and average ping times for each DNS server
- 🎯 **Smart Recommendations**: Automatically suggests the top 4 fastest DNS servers
- 💻 **Cross-Platform**: Works on macOS, Windows, and Linux
- 🔄 **Auto Configuration**: Applies DNS settings with a single confirmation
- 📝 **Timestamped Logging**: Detailed logs with timestamps for tracking
- 🧹 **DNS Cache Clearing**: Automatically clears DNS cache before and after configuration
- 🌍 **51 DNS Providers**: Tests servers from Cloudflare, Google, Quad9, OpenDNS, and many more

## 📋 Requirements

- Python 3.6 or higher
- Administrator/Root privileges (required to change DNS settings)

### Platform-Specific Requirements

- **macOS**: No additional requirements
- **Linux**: NetworkManager with `nmcli` command
- **Windows**: No additional requirements

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/dnsJumper.git
   cd dnsJumper
   ```

2. **No additional dependencies required!** The script uses only Python standard libraries.

## 📖 Usage

### Basic Usage

Run the script with administrator/root privileges:

**macOS/Linux:**
```bash
sudo python3 dns_jumper.py
```

**Windows:**
```powershell
# Run PowerShell or Command Prompt as Administrator
python dns_jumper.py
```

### What Happens

1. The script detects your operating system and active network interface
2. Clears your DNS cache for accurate testing
3. Tests all 51 DNS servers by pinging each one
4. Displays results sorted by performance
5. Recommends the top 4 fastest DNS servers
6. Asks for your confirmation before applying changes
7. Configures your system with the best DNS servers
8. Clears DNS cache again to apply changes immediately

## 📊 Example Output

```
[2025-11-05 14:30:00] macOS detected.
[2025-11-05 14:30:00] Active network interface: 'Wi-Fi'
[2025-11-05 14:30:00] Clearing DNS cache...
[2025-11-05 14:30:00] DNS cache cleared successfully.
[2025-11-05 14:30:01] Starting performance tests on 51 DNS servers...
[2025-11-05 14:30:01] This may take a few minutes...

[2025-11-05 14:30:01] [1/51] Testing DNS server: 1.1.1.1 (Cloudflare)
[2025-11-05 14:30:01] Testing 1.1.1.1...
[2025-11-05 14:30:02]   Ping 1/5 to 1.1.1.1: 5.23 ms
[2025-11-05 14:30:03]   Ping 2/5 to 1.1.1.1: 4.98 ms
...

============================================================
[2025-11-05 14:35:00] PERFORMANCE TEST RESULTS (48/51 servers responded)
============================================================
[2025-11-05 14:35:00] 1. 1.1.1.1          (Cloudflare) | Avg:   5.12ms | Min:   4.98ms | Max:   5.45ms
[2025-11-05 14:35:00] 2. 8.8.8.8          (Google)     | Avg:   6.34ms | Min:   6.01ms | Max:   6.89ms
[2025-11-05 14:35:00] 3. 9.9.9.9          (Quad9)      | Avg:   7.21ms | Min:   6.95ms | Max:   7.67ms
...

============================================================
[2025-11-05 14:35:00] TOP 4 RECOMMENDED DNS SERVERS:
============================================================
[2025-11-05 14:35:00] 1. 1.1.1.1 (Cloudflare) | Avg latency: 5.12ms
[2025-11-05 14:35:00] 2. 8.8.8.8 (Google)     | Avg latency: 6.34ms
[2025-11-05 14:35:00] 3. 9.9.9.9 (Quad9)      | Avg latency: 7.21ms
[2025-11-05 14:35:00] 4. 4.2.2.1 (Level3)     | Avg latency: 8.45ms

------------------------------------------------------------
[y/n] Apply these DNS settings? y
[2025-11-05 14:35:10] Setting DNS for 'Wi-Fi' to 1.1.1.1 8.8.8.8 9.9.9.9 4.2.2.1
[2025-11-05 14:35:10] Clearing DNS cache...
[2025-11-05 14:35:11] DNS cache cleared successfully.
[2025-11-05 14:35:11] DNS settings updated successfully!
```

## 🗂️ Customization

### Modify DNS Server List

Edit `dnsList.json` to add or remove DNS servers:

```json
{
  "list": [
    {
      "id": 1,
      "ip": "1.1.1.1",
      "company": "Cloudflare"
    },
    {
      "id": 2,
      "ip": "8.8.8.8",
      "company": "Google"
    }
  ]
}
```

### Adjust Testing Parameters

Edit these variables in `dns_jumper.py`:

```python
# Number of pings per DNS server
PINGS_PER_SERVER = 5

# Number of top DNS servers to recommend
TOP_DNS_COUNT = 4
```

## 🌐 Included DNS Providers

The tool tests DNS servers from these providers:

- Cloudflare (1.1.1.1, 1.0.0.1)
- Google (8.8.8.8, 8.8.4.4)
- Quad9 (9.9.9.9, 9.9.9.11)
- OpenDNS (208.67.222.222, 208.67.220.220)
- AdGuard DNS
- CleanBrowsing
- Norton ConnectSafe
- Yandex DNS
- Verisign
- Level3
- Neustar DNS
- And 40+ more!

See `dnsList.json` for the complete list.

## 🔧 Troubleshooting

### Permission Denied
Make sure you're running the script with administrator/root privileges:
- macOS/Linux: Use `sudo`
- Windows: Run as Administrator

### "Could not determine active network interface"
Make sure you have an active internet connection. For Linux users, ensure NetworkManager is installed.

### DNS Cache Not Clearing (Linux)
Install one of these packages:
```bash
# Ubuntu/Debian
sudo apt install systemd-resolved

# Or
sudo apt install nscd
```

## 📝 How It Works

1. **Detection**: Identifies your OS and network interface
2. **Cache Clearing**: Clears existing DNS cache
3. **Testing**: Sends ping requests to each DNS server
4. **Analysis**: Calculates min, max, and average latency
5. **Ranking**: Sorts servers by performance
6. **Configuration**: Applies the top 4 servers to your system

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool modifies your system's DNS settings. While it's designed to be safe, please:
- Backup your current DNS settings before use
- Understand that changing DNS servers may affect your internet connectivity
- Use at your own risk

## 🌟 Star History

If you find this tool useful, please consider giving it a star ⭐️

## 💬 Support

If you have any questions or issues, please open an issue on GitHub.

---

Made with ❤️ by [Your Name]
