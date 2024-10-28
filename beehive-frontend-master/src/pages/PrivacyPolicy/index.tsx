import { Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent } from 'react';
import { NavLink as Link } from 'react-router-dom';

import { ReportBug, Wrapper } from '../../shared';

const useStyles = makeStyles({
    content: {
        textAlign: 'left',
        margin: '20px',
        width: '80%',
        alignSelf: 'center'
    },
    header: {
        fontWeight: 600,
        textDecoration: 'underline'
    },
    subheader: {
        fontWeight: 600
    }
});

type Props = Record<string, never>;

const PrivacyPolicy: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();

    return (
        <Wrapper loading={false}>
            <div className={classes.content}>
                <Typography
                    variant="h3"
                    component="h1"
                >
                    Privacy Policy
                </Typography>
                <Typography component={'span'} >
                    Welcome to <Link to="www.caas.ai">www.caas.ai</Link> (together with its subdomains, and services, the &quot;Site&quot;). Thank you for choosing to be part of our community at Beehive Software Inc. (&quot;Company,&quot; &quot;we,&quot; &quot;us,&quot; or &quot;our&quot;). We are committed to protecting your personal information and your right to privacy. If you have any questions or concerns about this privacy notice or our practices with regard to your personal information, please contact us at support@caas.ai.
                    This privacy notice describes how we might use your information if you visit our website at http://www.caas.ai or engage with us in other related ways ― including any sales, marketing, or events.
                    In this privacy notice, if we refer to:
                    &quot;Website,&quot; we are referring to any website of ours that references or links to this policy
                    &quot;Services,&quot; we are referring to our Website, and other related services, including any sales, marketing, or events
                    The purpose of this privacy notice is to explain to you in the clearest way possible what information we collect, how we use it, and what rights you have in relation to it. If there are any terms in this privacy notice that you do not agree with, please discontinue use of our Services immediately.
                    Please read this privacy notice carefully, as it will help you understand what we do with the information that we collect.

                    <ol>
                        <li>
                            <Typography className={classes.header}>WHAT INFORMATION DO WE COLLECT?</Typography>
                            In Short: We collect personal information that you provide to us.<br /><br />
                            We collect personal information that you voluntarily provide to us when you register on the Website, express an interest in obtaining information about us or our products and Services, when you participate in activities on the Website (such as by posting messages in our online forums or entering competitions, contests or giveaways) or otherwise when you contact us.
                            The personal information that we collect depends on the context of your interactions with us and the Website, the choices you make and the products and features you use. The personal information we collect may include the following:
                            Personal Information Provided by You. We collect names; email addresses; job titles; usernames; passwords; contact preferences; billing addresses; and other similar information.
                            All personal information that you provide to us must be true, complete and accurate, and you must notify us of any changes to such personal information.
                            <br /><br />
                            <Typography className={classes.subheader}>Information automatically collected</Typography>
                            In Short: Some information — such as your Internet Protocol (IP) address and/or browser and device characteristics — is collected automatically when you visit our Website.<br /><br />
                            We automatically collect certain information when you visit, use or navigate the Website. This information does not reveal your specific identity (like your name or contact information) but may include device and usage information, such as your IP address, browser and device characteristics, operating system, language preferences, referring URLs, device name, country, location, information about how and when you use our Website and other technical information.
                            This information is primarily needed to maintain the security and operation of our Website and for our internal
                            This information is primarily needed to maintain the security and operation of our Website, and for our internal analytics and reporting purposes.
                            Like many businesses, we also collect information through cookies and similar technologies. The information we collect includes:
                            Log and Usage Data. Log and usage data is service-related, diagnostic, usage and performance information our servers automatically collect when you access or use our Website and which we record in log files. Depending on how you interact with us, this log data may include your IP address, device information, browser type and settings and information about your activity in the Website (such as the date/time stamps associated with your usage, pages and files viewed, searches and other actions you take such as which features you use), device event information (such as system activity, error reports (sometimes called &apos;crash dumps&apos;) and hardware settings).
                            Device Data. We collect device data such as information about your computer, phone, tablet or other device you use to access the Website. Depending on the device used, this device data may include information such as your IP address (or proxy server), device and application identification numbers, location, browser type, hardware model Internet service provider and/or mobile carrier, operating system and system configuration information.
                        </li>
                        <li>
                            <Typography className={classes.header}>HOW DO WE USE YOUR INFORMATION?</Typography>
                            In Short: We process your information for purposes based on legitimate business interests, the fulfillment of our contract with you, compliance with our legal obligations, and/or your consent.<br /><br />
                            We use personal information collected via our Website for a variety of business purposes described below. We process your personal information for these purposes in reliance on our legitimate business interests, in order to enter into or perform a contract with you, with your consent, and/or for compliance with our legal obligations. We indicate the specific processing grounds we rely on next to each purpose listed below.
                            We use the information we collect or receive:
                            To send administrative information to you. We may use your personal information to send you product, service and new feature information and/or information about changes to our terms, conditions, and policies.
                            To protect our Services. We may use your information as part of our efforts to keep our Website safe and secure (for example, for fraud monitoring and prevention).
                            To enforce our terms, conditions and policies for business purposes, to comply with legal and regulatory requirements or in connection with our contract.
                            To respond to legal requests and prevent harm. If we receive a subpoena or other legal request, we may need to inspect the data we hold to determine how to respond.
                        </li>
                        <li>
                            <Typography className={classes.header}>WILL YOUR INFORMATION BE SHARED WITH ANYONE?</Typography>
                            In Short: We only share information with your consent, to comply with laws, to provide you with services, to protect your rights, or to fulfill business obligations.<br /><br />
                            We may process or share your data that we hold based on the following legal basis:
                            Consent: We may process your data if you have given us specific consent to use your personal information for a specific purpose.
                            Legitimate Interests: We may process your data when it is reasonably necessary to achieve our legitimate business interests.
                            Performance of a Contract: Where we have entered into a contract with you, we may process your personal information to fulfill the terms of our contract.
                            Legal Obligations: We may disclose your information where we are legally required to do so in order to comply with applicable law, governmental requests, a judicial proceeding, court order, or legal process, such as in response to a court order or a subpoena (including in response to public authorities to meet national security or law enforcement requirements).
                            Vital Interests: We may disclose your information where we believe it is necessary to investigate, prevent, or take action regarding potential violations of our policies, suspected fraud, situations involving potential threats to the safety of any person and illegal activities, or as evidence in litigation in which we are involved.
                            More specifically, we may need to process your data or share your personal information in the following situations:
                            Business Transfers. We may share or transfer your information in connection with, or during negotiations of, any merger, sale of company assets, financing, or acquisition of all or a portion of our business to another company.
                        </li>
                        <li>
                            <Typography className={classes.header}>DO WE USE COOKIES AND OTHER TRACKING TECHNOLOGIES?</Typography>
                            In Short: We may use cookies and other tracking technologies to collect and store your information.<br /><br />
                            We may use cookies and similar tracking technologies (like web beacons and pixels) to access or store information. Specific information about how we use such technologies and how you can refuse certain cookies is set out in our Cookie Notice.
                        </li>
                        <li>
                            <Typography className={classes.header}>HOW LONG DO WE KEEP YOUR INFORMATION?</Typography>
                            In Short: We keep your information for as long as necessary to fulfill the purposes outlined in this privacy notice unless otherwise required by law.<br /><br />
                            We will only keep your personal information for as long as it is necessary for the purposes set out in this privacy
                            notice unless a longer retention period is required or permitted by law (such as tax accounting or other legal notice, unless a longer retention period is required or permitted by law (such as tax, accounting or other legal
                            requirements). No purpose in this notice will require us keeping your personal information for longer than the period of time in which users have an account with us.
                            When we have no ongoing legitimate business need to process your personal information, we will either delete or anonymize such information, or, if this is not possible (for example, because your personal information has been stored in backup archives), then we will securely store your personal information and isolate it from any further processing until deletion is possible.
                        </li>
                        <li>
                            <Typography className={classes.header}>HOW DO WE KEEP YOUR INFORMATION SAFE?</Typography>
                            In Short: We aim to protect your personal information through a system of organizational and technical security measures.<br /><br />
                            We have implemented appropriate technical and organizational security measures designed to protect the security of any personal information we process. However, despite our safeguards and efforts to secure your information, no electronic transmission over the Internet or information storage technology can be guaranteed to be 100% secure, so we cannot promise or guarantee that hackers, cybercriminals, or other unauthorized third parties will not be able to defeat our security, and improperly collect, access, steal, or modify your information. Although we will do our best to protect your personal information, transmission of personal information to and from our Website is at your own risk. You should only access the Website within a secure environment.
                        </li>
                        <li>
                            <Typography className={classes.header}>WHAT ARE YOUR PRIVACY RIGHTS?</Typography>
                            In Short: In some regions, such as the European Economic Area (EEA) and United Kingdom (UK), you have rights that allow you greater access to and control over your personal information. You may review, change, or terminate your account at any time.<br /><br />
                            In some regions (like the EEA and UK), you have certain rights under applicable data protection laws. These may include the right (i) to request access and obtain a copy of your personal information, (ii) to request rectification or erasure; (iii) to restrict the processing of your personal information; and (iv) if applicable, to data portability. In certain circumstances, you may also have the right to object to the processing of your personal information. To make such a request, please use the contact details provided below. We will consider and act upon any request in accordance with applicable data protection laws.
                            If we are relying on your consent to process your personal information, you have the right to withdraw your consent at any time. Please note however that this will not affect the lawfulness of the processing before its withdrawal, nor will it affect the processing of your personal information conducted in reliance on lawful processing grounds other than consent.
                            If you are a resident in the EEA or UK and you believe we are unlawfully processing your personal information, you also have the right to complain to your local data protection supervisory authority. You can find their contact details here: https://ec.europa.eu/justice/data-protection/bodies/authorities/index_en.htm.
                            If you are a resident in Switzerland, the contact details for the data protection authorities are available here: https://www.edoeb.admin.ch/edoeb/en/home.html.
                            If you have questions or comments about your privacy rights, you may email us at support@caas.ai.
                            <br /><br />
                            <Typography className={classes.subheader}>Account Information</Typography>
                            If you would at any time like to review or change the information in your account or terminate your account, you can: Contact us using the contact information provided.
                            Upon your request to terminate your account, we will deactivate or delete your account and information from our active databases. However, we may retain some information in our files to prevent fraud, troubleshoot problems, assist with any investigations, enforce our Terms of Use and/or comply with applicable legal requirements.
                            Cookies and similar technologies: Most Web browsers are set to accept cookies by default. If you prefer, you can usually choose to set your browser to remove cookies and to reject cookies. If you choose to remove cookies or reject cookies, this could affect certain features or services of our Website. To opt-out of interest-based advertising by advertisers on our Website visit http://www.aboutads.info/choices/.
                            Opting out of email marketing: You can unsubscribe from our marketing email list at any time by clicking on the unsubscribe link in the emails that we send or by contacting us using the details provided below. You will then be removed from the marketing email list — however, we may still communicate with you, for example to send you service-related emails that are necessary for the administration and use of your account, to respond to service requests, or for other non-marketing purposes. To otherwise opt-out, you may:
                            Contact us using the contact information provided.
                        </li>
                        <li>
                            <Typography className={classes.header}>CONTROLS FOR DO-NOT-TRACK FEATURES</Typography>
                            Most web browsers and some mobile operating systems and mobile applications include a Do-Not-Track (&quot;DNT&quot;) feature or setting you can activate to signal your privacy preference not to have data about your online browsing activities monitored and collected. At this stage no uniform technology standard for recognizing and implementing DNT signals has been finalized. As such, we do not currently respond to DNT browser signals or any other mechanism that automatically communicates your choice not to be tracked online. If a standard for online tracking is adopted that we must follow in the future, we will inform you about that practice in a revised version of this privacy notice.
                        </li>
                        <li>
                            <Typography className={classes.header}>DO CALIFORNIA RESIDENTS HAVE SPECIFIC PRIVACY RIGHTS?</Typography>
                            In Short: Yes, if you are a resident of California, you are granted specific rights regarding access to your personal information.<br /><br />
                            California Civil Code Section 1798.83, also known as the &quot;Shine The Light&quot; law, permits our users who are California residents to request and obtain from us, once a year and free of charge, information about categories of personal information (if any) we disclosed to third parties for direct marketing purposes and the names and addresses of all third parties with which we shared personal information in the immediately preceding calendar year. If you are a California resident and would like to make such a request, please submit your request in writing to us using the contact information provided below.
                            If you are under 18 years of age, reside in California, and have a registered account with the Website, you have the right to request removal of unwanted data that you publicly post on the Website. To request removal of such data, please contact us using the contact information provided below, and include the email address associated with your account and a statement that you reside in California. We will make sure the data is not publicly displayed on the Website, but please be aware that the data may not be completely or comprehensively removed from all our systems (e.g. backups, etc.).
                            <br /><br />
                            <Typography className={classes.subheader}>CCPA Privacy Notice</Typography>
                            The California Code of Regulations defines a &quot;resident&quot; as:
                            (1) every individual who is in the State of California for other than a temporary or transitory purpose and
                            (2) every individual who is domiciled in the State of California who is outside the State of California for a temporary or transitory purpose
                            All other individuals are defined as &quot;non-residents.&quot;
                            If this definition of &quot;resident&quot; applies to you, we must adhere to certain rights and obligations regarding your personal information.
                        </li>
                        <li>
                            <Typography className={classes.header}>HOW CAN YOU CONTACT US ABOUT THIS NOTICE?</Typography>
                            If you have questions or comments about this notice, you may email us at support@caas.ai or by post to:
                            Beehive Software Inc. 17770 Old Summit Rd Los Gatos, CA 95033 United States
                        </li>
                        <li>
                            <Typography className={classes.header}>HOW CAN YOU REVIEW, UPDATE, OR DELETE THE DATA WE COLLECT FROM YOU?</Typography>
                            Based on the applicable laws of your country, you may have the right to request access to the personal information we collect from you, change that information, or delete it in some circumstances. To request to review, update, or delete your personal information, please submit a request form by clicking here.
                        </li>
                    </ol>
                </Typography>
            </div>

            <ReportBug />
        </Wrapper>
    );
};

export default PrivacyPolicy;
