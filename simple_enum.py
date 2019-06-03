from pathlib import Path
import subprocess
import logging
import argparse


class Enumerate(object):
    def __init__(self, root_dir='~/simple-enum'):
        self.root_dir = Path(root_dir).expanduser().resolve()

    def _check_dirs(self):
        if not self.root_dir.exists():
            logging.debug(f"{self.root_dir} does not exist. Creating...")
            self.root_dir.mkdir(parents=True)

        if not self.target_dir.exists():
            logging.debug(f"{self.target_dir} does not exist. Creating...")
            self.target_dir.mkdir()

    def _check_for_subdomains(self):
        with open(self.amass_out, 'r') as amass_out:
            contents = amass_out.read()
            return contents.strip()

    def _setup(self, domain):
        self.target_dir = Path(f"{self.root_dir}/{domain}").resolve()
        self.amass_out = Path(f"{self.target_dir}/amass.out").resolve()
        self.aquatone_out = Path(f"{self.target_dir}/aquatone").resolve()
        self._check_dirs()

    def _process_args(self, args):
        if args.domain_file:
            with open(args.domain_file, 'r') as file:
                self.domains = file.read().splitlines()
        elif args.domain:
            self.domains = [args.domain]

    def enumerate(self, args):
        self._process_args(args)
        for domain in self.domains:
            logging.info(f"Running subdomain enumeration against:\t{domain}")
            self._setup(domain)
            cmd = f"amass enum -d {domain} -r 1.1.1.1,8.8.8.8 -o {self.amass_out}"
            try:
                p = subprocess.run(cmd, check=True, shell=True, capture_output=True)
            except subprocess.CalledProcessError:
                logging.error('Amass returned non-zero return code.', exc_info=True)
                logging.debug(f"Command run: {cmd} - Output: {p.stdout} | {p.stderr}")
            logging.info(f"Finished enumeration. You can view results at: {self.amass_out}")

    def capture(self, args):
        self._process_args(args)
        for domain in self.domains:
            self._setup(domain)
            logging.info(f"Running screenshot capture against:\t{domain}")
            if self._check_for_subdomains():
                cmd = f"cat {self.amass_out} | aquatone -scan-timeout 500 -ports large -out {self.aquatone_out}"
                try:
                    p = subprocess.run(cmd, check=True, shell=True, capture_output=True)
                except subprocess.CalledProcessError:
                    logging.error('Aquatone returned non-zero return code.', exc_info=True)
                    logging.debug(f"Command run: {cmd} - Output: {p.stdout} | {p.stderr}")
                logging.info(f"Finished capturing. You can view results at: {self.aquatone_out}/aquatone_report.html")
            else:
                logging.warning('No subdomains found. Skipping screenshotting...')

    def scan(self, args):
        self.enumerate(args)
        self.capture(args)


def setup_logging(log_level):
    logging.basicConfig(
        level=log_level,
        format='%(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('simple-enum.log', mode='w'),
            logging.StreamHandler()
        ]
    )


def setup_parsing():
    parser = argparse.ArgumentParser(
        prog='simple_enum.py',
        description='Simply enumerate your targets.'
    )
    subparsers = parser.add_subparsers(
        title='Enumeration task',
        dest='task'
    )
    parser.add_argument(
        '-d',
        '--dir',
        default='~/simple-enum',
        help='Location of the root directory to store results. Default=~/simple-enum'
    )
    parser.add_argument(
        '--debug',
        help='Sets logger level to debug',
        default=logging.INFO,
        action='store_const',
        const=logging.DEBUG,
        dest='log_level'
    )

    parent_parser = argparse.ArgumentParser(add_help=False)
    group = parent_parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--domain', help='Domain to enumerate')
    group.add_argument('-df', '--domain-file', help='File containing domains to enumerate (newline separated)')

    subparsers.add_parser('scan', parents=[parent_parser])
    subparsers.add_parser('enumerate', parents=[parent_parser])
    subparsers.add_parser('capture', parents=[parent_parser])

    return parser


if __name__ == '__main__':
    parser = setup_parsing()
    args = parser.parse_args()
    setup_logging(args.log_level)

    if args.task:
        enum = Enumerate(args.dir)
        getattr(enum, args.task)(args)
    else:
        parser.print_help()
