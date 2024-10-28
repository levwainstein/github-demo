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

const TermsOfUse: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();

    return (
        <Wrapper loading={false}>
            <div className={classes.content}>
                <Typography
                    variant="h3"
                    component="h1"
                >
                    Terms of Use
                </Typography>
                <Typography component={'span'} >
                    Welcome to <Link to="www.caas.ai">www.caas.ai</Link> (together with its subdomains, and services, the &quot;Site&quot;). Please read the following Terms of Use carefully before using this Site so that you are aware of your legal rights and obligations with respect to Beehive Software Inc. (&quot;Company&quot;,  &quot;we&quot;, &quot;our&quot; or &quot;us&quot;). By accessing or using the Site, you expressly acknowledge and agree that you are entering a legal agreement with us and have understood and agree to comply with, and be legally bound by, these Terms of Use, together with the Privacy Policy available at <Link to="privacy-policy">https://app.caas.ai/privacy-policy</Link> (collectively, &quot;Terms&quot;). You hereby waive any applicable rights to require an original (non-electronic) signature or delivery or retention of non-electronic records, to the extent not prohibited under applicable law. If you do not agree to be bound by these Terms please do not access or use the Site.
                    <br /><br />
                    NOW, THEREFORE, the parties hereby agree as follows:
                    <br />
                    <ol>
                        <li>
                            <Typography className={classes.header}>Definitions.</Typography>
                            For purposes of these Terms, the following capitalized terms shall have the following meaning:
                            <ol>
                                <li>&quot;Confidential Information&quot; means all non-public information, in any form whatsoever, tangible or intangible, including information in oral, visual, or computer database form, disclosed by the Company to you. Confidential Information shall include any such information concerning past, present, or future ideas, research and development, know-how, trade secrets, inventions, formulas, specifications, compositions, manufacturing, and production processes and techniques, technical data, code, technology, and/or product designs, drawings, engineering, and/or development specifications, business and marketing plans, forecasts and projections, financial data, or any other business activities. Confidential Information shall also include Intellectual Property and technology, including any processes, methodologies, procedures, trade secrets, software, software applications, tools, databases, systems architecture and design, machine-readable texts and files, literary works or other works of authorship, including documentation, reports, drawings, charts, graphics and other written documentation, whether or not owned by the Company, provided to you by or through the Company. However, Confidential Information shall not include information that is: (i) publicly available or becomes publicly available through no act or omission of you or anyone else on your behalf; (ii) legitimately obtained by you without restriction, from a source other than the Company; or (iii) explicitly approved for release by written authorization of the Company. Any combination of features shall not be deemed to be within the foregoing exceptions merely because individual features thereof are in the public domain or in your possession, but only if the combination itself and its principle of operation are in the public domain or in your possession. For the avoidance of doubt, the Deliverables shall be deemed Company&apos;s Confidential Information.</li>
                                <li>&quot;Deliverables&quot; means all code, documentation, and other materials produced as a result of the Services (as defined hereunder) and delivered to the Company by you in the course of providing the Services pursuant to these Terms.</li>
                                <li>&quot;Intellectual Property&quot; means all intangible legal rights, titles, and interests evidenced by or embodied in or connected or related to: (i) all Inventions (whether patentable or unpatentable and whether or not reduced to practice), all improvements thereto, and all patents, patent applications and patent disclosures, together with all reissuances, continuations, continuations-in-part, revisions, extensions, and reexaminations thereof; (ii) all trademarks, service marks, trade dress, logos, trade names, corporate names, domain names together with all translations, adaptations, derivations, and combinations thereof and including all goodwill associated therewith, and all applications, registrations, and renewals in connection therewith; (iii) any work of authorship, regardless of copyrightability, all compilations, all copyrightable works, all copyrights (including moral rights) and all applications, registrations and renewals in connection therewith; (iv) all mask works and all applications, registrations, and renewals in connection therewith; (v) all trade secrets, Confidential Information and business information; (vi) all computer software (including data and related documentation), source code, and any other related documentation; and (vii) all other proprietary rights, industrial rights, and any other similar rights, in each case on a worldwide basis, and all copies and tangible embodiments thereof, or any part thereof, in whatever form or medium.</li>
                                <li>&quot;Invention&quot; means any idea, design, concept, technique, invention, discovery or improvement, regardless of patentability, made solely or jointly by you, produced by or for you, or made jointly by you with one or more employees of Company, during the Term (as defined hereunder) and in performance of any work under these Terms.</li>
                                <li>&quot;Specifications&quot; means the functional specifications for the Deliverables per the Company&apos;s Task (as defined below), as they may appear in the Site.</li>
                            </ol>
                        </li>
                        <li>
                            <Typography className={classes.header}>Services.</Typography>
                            You agree to provide to the Company the programming and developing services specified in the Specifications (&quot;Services&quot;).
                        </li>
                        <li>
                            <Typography className={classes.header}>Changes.</Typography>
                            Changes in any of the Specifications or Deliverables under any Task  shall become effective only when a written change request is executed by authorized representatives of both parties.
                        </li>
                        <li>
                            <Typography className={classes.header}>Delivery and Testing.</Typography>
                            <ol>
                                <li>Delivery. You shall complete and deliver to Company any Deliverable in accordance with the applicable task Company sets out for you on the Site (&quot;Task&quot;). It is hereby clarified that the Company is under no obligation to provide you with any Tasks. </li>
                                <li>Testing. Company may supervise and test the completion of the Task following receipt of the Deliverables, to ascertain whether the Deliverables operate in accordance with the Specifications of the Task. During such testing, the Company shall notify you of any inconsistencies with the Specifications. Upon completion of such testing, the Company shall notify you if the Task has been completed successfully. In the event you have failed to complete the Task, you shall use all reasonable effort to correct any deficiencies or non-conformities and resubmit the rejected items as promptly as possible.</li>
                                <li>Acceptance. Acceptance of the Deliverables shall occur upon the successful completion of the Task and receipt by you of Company&apos;s acceptance and full satisfaction of the Deliverables.</li>
                            </ol>
                        </li>
                        <li>
                            <Typography className={classes.header}>Compensation.</Typography>
                            <ol>
                                <li>Method of Payment. Amounts, method of payment, and terms of payment for all Services to be performed and Deliverables to be delivered, shall be set on a case-by-case basis and in accordance with each Task.</li>
                                <li>Taxes. Except as expressly agreed upon between the parties, the prices set forth and agreed upon between the parties shall include all taxes however designated and levied by any state, local or government agency (including sales taxes and VAT). Company shall be entitled to withhold any amounts required to be withheld by any applicable law.</li>
                                <li>Expenses. You shall bear all of your own expenses arising from your performance or your obligations under these Terms.</li>
                            </ol>
                        </li>
                        <li>
                            <Typography className={classes.header}>Rights in Deliverables.</Typography>
                            Title to all Deliverables and Inventions and all Intellectual Property rights and interest attached/connected/related thereto (&quot;Proprietary Materials&quot;) will vest in Company and such Proprietary Materials will be deemed &quot;works made for hire&quot; by you for the benefit of Company. You hereby assign, transfer and convey to the Company all right, title, and interest in and to such Proprietary Materials. You shall not represent that it possesses any proprietary interest in the Proprietary Materials and shall not, directly or indirectly, take any action to contest Company&apos;s Intellectual Property rights, or infringe them in any way. Notwithstanding the foregoing, to the extent that any such Proprietary Materials may not be considered works made for hire, all rights, title, and interest therein, including all renewals and extensions thereof, are hereby irrevocably assigned to the Company. All such Proprietary Materials will belong exclusively to the Company, with the Company having the right to obtain and to hold in its own name, copyrights, trademarks, patents, registrations or such other protection as may be appropriate to the subject matter, and any extensions and renewals thereof. If you include in the Proprietary Materials preexisting works owned or licensed by it, you shall identify such works prior to commencement of the, and you hereby grant the Company a non-exclusive, perpetual worldwide right and license to use, execute, sublicense, reproduce and prepare derivative works based upon such works. You agree to give the Company and any other person designated by the Company, reasonable assistance, at Company&apos;s expense, required to perfect the rights defined in this Section. Without derogating from any of the above, you agree that it shall not be entitled, and hereby explicitly waives now and/or in the future, any claim, to any right, compensation, royalty, and/or reward in connection with the Proprietary Materials. During the Term and at all times thereafter, you agree to, and further agree to make sure that any of your employees agrees to, give evidence and execute such documents as Company may reasonably request and to warrant and confirm Company&apos;s title to and ownership of all such results and proceeds, and to transfer and assign to Company any rights which you may have therein.
                        </li>
                        <li>
                            <Typography className={classes.header}>Confidential Information.</Typography>
                            You shall refrain from using or exploiting the Confidential Information for any purposes or activities other than for the performance of these Terms. You shall: (i) keep the Confidential Information confidential using at least the same degree of care you use to protect your own confidential information, which shall in any event not be less than a reasonable degree of care; (ii) refrain from disclosing or facilitating disclosure of Confidential Information to anyone, without Company&apos;s prior written consent; (iii) immediately notify the Company in the event of any loss or unauthorized disclosure of any Confidential Information; (iv) not to use Confidential Information otherwise for your own or any third party&apos;s benefit without the prior written approval of an authorized representative of the Company in each instance; (v) not reverse engineer, decompile or disassemble any Confidential Information disclosed to you by the Company; and (vi) not make any copies of the Confidential Information on any type of media, without the prior express written permission of the authorized representative of the Company. If you are required by an order of a court, administrative agency or other government body, to disclose Confidential Information, you shall provide the Company with prompt written notice of such order to enable the Company to seek a protective order or otherwise prevent or restrict such disclosure, and shall reasonably cooperate with the Company in its efforts to obtain such protective order at the sole cost and expense of the Company. The obligations of confidentiality under these Terms shall survive the termination of these Terms.
                        </li>
                        <li>
                            <Typography className={classes.header}>Warranties and Representations.</Typography>
                            You hereby represent and warrant that: (i) you have the requisite technical and professional knowledge, know-how, expertise, skills, talent, and experience required in order to perform the Services in a professional and efficient manner; (ii) there are no restrictions, limitations, contractual obligations or statutory obligations or restrictions or any other factor whatsoever which prevents or restricts or is likely to prevent or restrict you from fulfilling all your obligations under these Terms and the performance of the Services, and delivering the Deliverables in accordance with the time frame agreed upon between you and Company; (iii) the execution of these Terms by you and the performance of the obligations hereunder shall not constitute or result in a breach of any of your other obligations, contractual or otherwise; (iv) in the performance of the Services, you will fully comply with all applicable laws, regulations and ordinances; (v) all copyrightable matter assigned and/or licensed in accordance with these Terms have been or will be created by you and no third party has or will have &quot;moral rights&quot; or rights to terminate any assignment or license with respect thereto; (vi) all development work including but not limited to the Deliverables shall be prepared without knowingly breaching any third party Intellectual Property rights and in a workmanlike manner and with professional diligence and skill and will conform to the Specifications relating thereto; (vii) that the provision of Services does not and shall not conflict with any other activities or services provided by you to any third parties; and (viii) you will inform the Company, immediately after becoming aware of any matter that may in any way raise a conflict of interest between you and the Company. Without derogating from any other rights under this Agreement or at law, the Company may require you to cease to have any such personal interest or conflict of interest, as the case may be.
                        </li>
                        <li>
                            <Typography className={classes.header}>Prohibited Uses.</Typography>
                            Except as specifically permitted herein, without the prior written consent of the Company, you represent and warrant that you must not, and shall not: (i) sell, license (or sub-license), lease, assign, transfer, pledge, or share your rights and obligations under these Terms with any third party; (ii) use any &quot;open source&quot; or &quot;copyleft software&quot; in a manner that would require the Company to disclose the source code of the Site and/or the Deliverables to any third party; (iii) disassemble, decompile, reverse engineer or attempt to discover the Site&apos;s source code or underlying algorithms; (iv) remove or alter any trademarks or other proprietary notices related to the Site; (v) transmit any malicious code (i.e., software viruses, Trojan horses, worms, malware or other computer instructions, devices or techniques that erase data or programming, infect, disrupt, damage, disable or shut down a computer system or any component of such computer system) or other unlawful material in connection with the Site and/or the Deliverables.
                        </li>
                        <li>
                            <Typography className={classes.header}>Warranty Disclaimers.</Typography>
                            <ol>
                                <li>THE SITE IS PROVIDED ON AN &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; BASIS, AND WITHOUT WARRANTIES OF ANY KIND EITHER EXPRESS OR IMPLIED. COMPANY HEREBY DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, TITLE, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND THOSE ARISING BY STATUTE OR FROM A COURSE OF DEALING OR USAGE OF TRADE. COMPANY DOES NOT GUARANTEE THAT THE SITE WILL BE FREE OF BUGS, SECURITY BREACHES, OR VIRUS ATTACKS. THE SITE MAY OCCASIONALLY BE UNAVAILABLE FOR ROUTINE MAINTENANCE, UPGRADING OR OTHER REASONS. YOU AGREE THAT COMPANY WILL NOT BE HELD RESPONSIBLE FOR ANY CONSEQUENCES TO YOU OR ANY THIRD PARTY THAT MAY RESULT FROM TECHNICAL PROBLEMS OF THE INTERNET, SLOW CONNECTIONS, TRAFFIC CONGESTION OR OVERLOAD OF OUR OR OTHER SERVERS. WE DO NOT WARRANT, ENDORSE OR GUARANTEE ANY CONTENT, PRODUCT OR SERVICE THAT IS FEATURED OR ADVERTISED ON THE SITE BY A THIRD PARTY.</li>
                                <li>EXCEPT AS EXPRESSLY STATED IN OUR PRIVACY POLICY, COMPANY DOES NOT MAKE ANY REPRESENTATIONS, WARRANTIES OR CONDITIONS OF ANY KIND, EXPRESS OR IMPLIED, AS TO THE SECURITY OF ANY INFORMATION YOU MAY PROVIDE OR ACTIVITIES YOU ENGAGE IN DURING THE COURSE OF YOUR USE OF THE SITE.</li>
                            </ol>
                        </li>
                        <li>
                            <Typography className={classes.header}>Indemnification.</Typography>
                            You agree to indemnify, defend and hold harmless the Company and its officers, directors, employees, agents, successors, and assigns, from any and all losses, liabilities, damages and claims, and all related costs and expenses (including reasonable legal fees and disbursements and costs of investigation, litigation, settlement, judgment, interest and penalties) arising from, in connection with, or based on allegations whenever made of, the breach of any representation or warranty made by you under Sections 8 and 9.
                        </li>
                        <li>
                            <Typography className={classes.header}>Limitation of Liabilities.</Typography>
                            THE PARTIES SHALL NOT BE LIABLE (WHETHER UNDER CONTRACT, TORT (INCLUDING NEGLIGENCE) OR ANY OTHER LEGAL THEORY) FOR ANY INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES, INCLUDING, ANY LOSS OR DAMAGE TO BUSINESS EARNINGS, LOST PROFITS OR GOODWILL, SUFFERED BY ANY PERSON, ARISING FROM AND/OR RELATED WITH THESE TERMS, EVEN IF SUCH PARTY IS ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
                            <br />
                            The limitations set forth above will not apply with respect to damages occasioned by: (i) your willful misconduct, unlawful conduct or gross negligence; (ii) claims that are the subject of indemnification under these Terms; or (iii) damages caused by your breach of your obligations with respect to Confidential Information.
                        </li>
                        <li>
                            <Typography className={classes.header}>Term and Termination.</Typography>
                            These Terms are effective until terminated by the Company or you. Company, in its sole discretion, has the right to terminate these Terms and/or your access to the Site, or any part thereof, immediately at any time and with or without cause (including, without any limitation, for a breach of these Terms). Company shall not be liable to you or any third party for termination of the Site, or any part thereof. If you object to any term or condition of these Terms, or any subsequent modifications thereto, or become dissatisfied with the Site in any way, your only recourse is to immediately discontinue use of the Site. Upon termination of these Terms, you shall cease all use of the Site. Upon receipt of notice of such termination (or upon your termination of these Terms), you shall inform Company of the extent of which performance has been completed through such date, and collect and deliver to Company whatever Deliverables which then exist in a manner prescribed by Company. You shall be paid for all work actually performed through the date of termination, provided that such payment shall not be greater than the payment that would have become due if the applicable Tasks have been completed. This Section 13 and Sections 1, 6, 7, 10, 11, 12, 14 and 15 ‎ shall survive termination of these Terms.
                        </li>
                        <li>
                            <Typography className={classes.header}>Status of Parties.</Typography>
                            You and Company are independent contractors. Nothing in these Terms creates a partnership, joint venture, agency or employment relationship between you and Company. You must not under any circumstances make or undertake any warranties, representations, commitments or obligations on behalf of the Company.
                        </li>
                        <li>
                            <Typography className={classes.header}>Miscellaneous.</Typography>
                            These Terms, and any rights and licenses granted hereunder, may not be transferred or assigned by you but may be assigned by Company without restriction or notification to you. Company reserves the right to discontinue or modify any aspect of the Site at any time. These Terms and the relationship between you and Company shall be governed by and construed in accordance with the laws of the State of New York, without regard to its principles of conflict of laws. You agree to submit to the personal and exclusive jurisdiction of the courts located in New York County, NY and waive any jurisdictional, venue or inconvenient forum objections to such courts, provided that Company may seek injunctive relief in any court of competent. These Terms shall constitute the entire agreement between you and Company concerning the Site and any Tasks performed hereunder. If any provision of these Terms is deemed invalid by a court of competent jurisdiction, the invalidity of such provision shall not affect the validity of the remaining provisions of these Terms, which shall remain in full force and effect. No waiver of any term of these Terms shall be deemed a further or continuing waiver of such term or any other term, and a party&apos;s failure to assert any right or provision under these Terms shall not constitute a waiver of such right or provision. YOU AGREE THAT ANY CAUSE OF ACTION THAT YOU MAY HAVE ARISING OUT OF OR RELATED TO THE SITE MUST COMMENCE WITHIN 1 YEAR AFTER THE CAUSE OF ACTION ACCRUES. OTHERWISE, SUCH CAUSE OF ACTION IS PERMANENTLY BARRED.
                        </li>
                    </ol>
                </Typography>
            </div>

            <ReportBug />
        </Wrapper>
    );
};

export default TermsOfUse;
