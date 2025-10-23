import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function AboutPage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold">About</h1>
        <p className="text-muted-foreground mt-2">
          Learn more about the Solar Burst Identification project.
        </p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Project Background</CardTitle>
            <CardDescription>
              Origin and purpose of the Solar Burst Identification system.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              This project was developed to provide automated tools for detecting and characterizing solar bursts in X-ray light curves.
              Solar bursts, also known as solar flares, are sudden releases of energy that can affect space weather and satellite communications.
            </p>
            <p className="text-muted-foreground">
              The system is designed to process data from X-ray observatories, particularly those monitoring solar activity in soft X-ray bands.
              It implements established algorithms for burst detection and parameter extraction, making solar flare analysis more accessible to researchers.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contributors</CardTitle>
            <CardDescription>
              People and organizations involved in the project.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold">Development Team</h3>
                <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                  <li>Lead Developer: [Your Name]</li>
                  <li>Scientific Advisor: [Advisor Name]</li>
                  <li>UI/UX Designer: [Designer Name]</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold">Affiliations</h3>
                <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                  <li>Department of Astronomy, [University Name]</li>
                  <li>[Research Institute Name]</li>
                  <li>ISRO Solar X-ray Monitor (XSM) Team</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>References</CardTitle>
            <CardDescription>
              Scientific references and related missions.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold">Related Missions</h3>
                <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                  <li>ISRO's XSM (X-ray Solar Monitor) on Astrosat</li>
                  <li>GOES X-ray Sensor</li>
                  <li>RHESSI (Reuven Ramaty High Energy Solar Spectroscopic Imager)</li>
                  <li>SDO (Solar Dynamics Observatory) / AIA</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold">Scientific Publications</h3>
                <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                  <li>Yoshida et al. (2020) - Solar flare detection algorithms</li>
                  <li>Hannah et al. (2011) - RHESSI flare catalog</li>
                  <li>Fletcher et al. (2011) - Solar flare observations review</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Licensing</CardTitle>
            <CardDescription>
              Open-source terms and usage rights.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-muted-foreground">
                This project is released under the MIT License, allowing free use, modification, and distribution for both academic and commercial purposes.
              </p>
              <div>
                <h3 className="font-semibold">License Summary</h3>
                <p className="text-sm text-muted-foreground">
                  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files,
                  to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish,
                  distribute, sublicense, and/or sell copies of the Software.
                </p>
              </div>
              <div>
                <h3 className="font-semibold">Attribution</h3>
                <p className="text-sm text-muted-foreground">
                  If you use this software in your research, please cite the project repository and acknowledge the contributors.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
