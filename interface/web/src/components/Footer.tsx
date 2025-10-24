import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Solar Burst Identification. Licensed under MIT.
          </div>
          <div className="flex items-center space-x-4 mt-4 md:mt-0">
            <div className="flex space-x-4">
              <Link href="/docs" className="text-sm text-muted-foreground hover:underline">
                Docs
              </Link>
              <a
                href="https://github.com/priyanshsingh-dev/Identification-Of-Solar-Bursts-IN-X-Ray-Light-Curves"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:underline"
              >
                GitHub
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
