import { PageHeading } from "@/components/page-heading";
import { SettingsPanel } from "@/components/settings-panel";
export default function SettingsPage() { return <><PageHeading eyebrow="Runtime configuration" title="System settings" description="Read-only operational details reported by the backend. Environment secrets are never exposed." backHref="/" /><SettingsPanel /></>; }

