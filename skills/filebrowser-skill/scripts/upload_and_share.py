#!/usr/bin/env python3
"""
上传单个文件并获取分享链接
"""

import os
import argparse
import requests
from typing import Optional, Dict


class FileBrowserClient:
    """FileBrowser API 客户端"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.session = requests.Session()

    def login(self) -> bool:
        """登录获取 JWT Token"""
        url = f"{self.base_url}/api/login"
        data = {
            "username": self.username,
            "password": self.password
        }
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                self.token = response.text.strip()
                self.session.headers.update({"X-Auth": self.token})
                print(f"✅ 登录成功: {self.username}")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False

    def upload_file(self, local_path: str, remote_path: str, override: bool = False) -> bool:
        """上传文件到云端"""
        url = f"{self.base_url}/api/resources{remote_path}"
        params = {"override": str(override).lower()}

        try:
            with open(local_path, 'rb') as f:
                response = self.session.post(url, data=f, params=params)
                if response.status_code == 200:
                    print(f"✅ 上传成功: {remote_path}")
                    return True
                elif response.status_code == 409:
                    print(f"⚠️ 文件已存在: {remote_path}")
                    return False
                else:
                    print(f"❌ 上传失败: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"❌ 上传异常: {e}")
            return False

    def create_share(self, remote_path: str, expires: str = None, unit: str = None, password: str = None) -> Optional[Dict]:
        """创建分享链接"""
        url = f"{self.base_url}/api/share{remote_path}"
        data = {}

        if expires and unit:
            data["expires"] = expires
            data["unit"] = unit
        if password:
            data["password"] = password

        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 创建分享失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 创建分享异常: {e}")
            return None

    def get_share_links(self, hash: str) -> Dict[str, str]:
        """根据 hash 生成各类访问链接"""
        return {
            "preview": f"{self.base_url}/share/{hash}",
            "download": f"{self.base_url}/api/public/dl/{hash}",
            "direct": f"{self.base_url}/api/public/dl/{hash}?inline=true"
        }


def main():
    parser = argparse.ArgumentParser(
        description="上传单个文件并获取分享链接",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 上传文件并创建永久分享
  python upload_and_share.py --url http://localhost:8080 --user admin --password pwd --file ./report.pdf

  # 上传文件并创建24小时有效的分享
  python upload_and_share.py --url http://localhost:8080 --user admin --password pwd --file ./report.pdf --expires 24 --unit hours

  # 上传文件并创建带密码保护的分享
  python upload_and_share.py --url http://localhost:8080 --user admin --password pwd --file ./report.pdf --password secret123

  # 上传到指定远程路径
  python upload_and_share.py --url http://localhost:8080 --user admin --password pwd --file ./report.pdf --remote /documents/report.pdf
        """
    )

    parser.add_argument("--url", required=True, help="FileBrowser 服务地址")
    parser.add_argument("--user", required=True, help="用户名")
    parser.add_argument("--password", required=True, help="密码")
    parser.add_argument("--file", required=True, help="本地文件路径")
    parser.add_argument("--remote", help="远程路径（默认使用文件名）")
    parser.add_argument("--expires", help="过期时间数值")
    parser.add_argument("--unit", choices=["seconds", "minutes", "hours", "days"], help="时间单位")
    parser.add_argument("--share-password", dest="share_password", help="分享密码保护")
    parser.add_argument("--override", action="store_true", help="覆盖已存在的文件")

    args = parser.parse_args()

    # 确定远程路径
    if args.remote:
        remote_path = args.remote
    else:
        filename = os.path.basename(args.file)
        remote_path = f"/{filename}"

    # 创建客户端并登录
    client = FileBrowserClient(args.url, args.user, args.password)
    if not client.login():
        return

    # 上传文件
    if not client.upload_file(args.file, remote_path, args.override):
        print("❌ 上传失败，无法创建分享")
        return

    # 创建分享
    share_info = client.create_share(
        remote_path,
        expires=args.expires,
        unit=args.unit,
        password=args.share_password
    )

    if share_info:
        links = client.get_share_links(share_info["hash"])

        print("\n📋 分享链接:")
        print(f"  预览链接: {links['preview']}")
        print(f"  下载链接: {links['download']}")
        print(f"  直接查看: {links['direct']}")

        if args.expires and args.unit:
            print(f"  有效期: {args.expires} {args.unit}")

        if args.share_password:
            print(f"  密码保护: {args.share_password}")
            print("  访问者需要输入密码才能访问")


if __name__ == "__main__":
    main()