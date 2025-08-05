# Synthetic Email Dataset Generation Specification

## Project Context and Narrative

### Construction Project Background
**Project**: Riverside Community Center Construction  
**Timeline**: January 2024 - August 2024  
**Status**: Delayed due to multiple issues  
**Budget**: $2.3M original, with change orders  

### Key Project Issues (Email Content Drivers)
1. **Roof Leak Discovery**: Found during framing inspection in March 2024
2. **Change Order #3**: Major electrical upgrade required, disputed approval
3. **Contractor Delays**: Weather delays and material shortages
4. **Personnel Issues**: Project manager reassignment mid-project
5. **Legal Consultations**: Attorney involvement in contract disputes

### Project Participants (Email Personas)

#### City Agency Staff
- **Sarah Chen** (sarah.chen@riverside.gov) - Project Manager (until April)
- **Mike Rodriguez** (mike.rodriguez@riverside.gov) - Senior Engineer  
- **Jennifer Walsh** (jennifer.walsh@riverside.gov) - New Project Manager (from May)
- **David Kim** (david.kim@riverside.gov) - Facilities Director
- **Lisa Thompson** (lisa.thompson@riverside.gov) - HR Representative

#### Legal Counsel
- **Robert Sterling** (robert.sterling@sterlingmunicipallaw.com) - City Attorney
- **Amanda Foster** (amanda.foster@contractordefense.com) - Contractor's Attorney

#### Contractor Team
- **Tony Martinez** (tony.martinez@eliteconstructionco.com) - Project Superintendent
- **Rachel Green** (rachel.green@eliteconstructionco.com) - Contract Administrator
- **Steve Wilson** (steve.wilson@eliteconstructionco.com) - Site Foreman

#### Consultants/Vendors
- **Dr. James Liu** (james.liu@structuralengineers.com) - Structural Engineer
- **Maria Santos** (maria.santos@electricalconsulting.com) - Electrical Consultant

---

## Email Generation Requirements

### Dataset Composition (30 Emails Total)

#### Responsiveness Distribution
- **Responsive to Request 1 (Roof Leak)**: 8 emails
- **Responsive to Request 2 (Change Order #3)**: 9 emails  
- **Responsive to Request 3 (Internal Delays)**: 7 emails
- **Non-Responsive**: 6 emails

#### Exemption Distribution
- **Attorney-Client Privilege**: 4 emails (clearly identifiable)
- **Personnel Records**: 3 emails (containing employee information)
- **Deliberative Process**: 4 emails (internal decision-making)
- **No Exemptions**: 19 emails

#### Email Structure Distribution
- **Individual Emails**: 21 emails (70%)
- **Email Chains**: 3 chains of 2-4 emails each (9 total emails, 30%)

### Standard Email Format Template

**IMPORTANT**: The email parser expects emails to be separated by starting each new email with `From:` at the beginning of a line. Do not use separator lines between emails. Simply start each new email with the `From:` header.

```
From: sender.name@domain.com
To: recipient.name@domain.com
CC: optional.cc@domain.com
Subject: Subject Line Here
Date: Mon, 15 Jan 2024 09:30:00 -0800

Email body content starts here after a blank line.

Can include multiple paragraphs and formatting.

Signature lines at the end if appropriate.

From: next.sender@domain.com
To: next.recipient@domain.com
Subject: Next Email Subject
Date: Wed, 17 Jan 2024 14:20:00 -0800

Next email body starts here...
```

### Email Chain Format Template

For email chains, format them as consecutive emails with reply subjects. Each email in the chain should be a complete email with all headers:

```
From: original.sender@domain.com
To: recipient@domain.com
Subject: Original Subject
Date: Mon, 15 Jan 2024 09:30:00 -0800

Original email body content here...

From: reply.sender@domain.com  
To: original.sender@domain.com
Subject: RE: Original Subject
Date: Mon, 15 Jan 2024 10:45:00 -0800

Reply content here, potentially quoting original...

> Original message quoted if appropriate

New response content...
```

---

## Specific Email Content Requirements

### Request 1: Roof Leak Documents (8 emails)
**CPRA Request**: "All documents regarding the roof leak issues on the Community Center construction project"

**Required Emails**:
1. **Discovery Email** (Responsive, No Exemption)
   - From: Mike Rodriguez to project team
   - Subject: "URGENT: Water intrusion discovered in north wing"
   - Content: Initial discovery of leak during inspection

2. **Engineering Assessment** (Responsive, No Exemption)
   - From: Dr. James Liu to Sarah Chen
   - Subject: "Structural assessment - roof leak damage"
   - Content: Professional assessment of structural impact

3. **Legal Consultation** (Responsive, Attorney-Client Privilege)
   - From: Robert Sterling to David Kim
   - Subject: "PRIVILEGED: Legal implications of roof leak delay"
   - Content: Legal advice on contract implications, liability

4. **Internal Deliberation** (Responsive, Deliberative Process)
   - From: Sarah Chen to David Kim
   - Subject: "DRAFT: Options for addressing roof leak"
   - Content: Internal strategy discussion, decision alternatives

5. **Contractor Notification** (Responsive, No Exemption)
   - From: Sarah Chen to Tony Martinez
   - Subject: "Roof leak remediation requirements"
   - Content: Formal notification to contractor about issue

6. **Cost Estimate Chain** (Responsive, No Exemption, 2-email chain)
   - Email 1: Request for repair cost estimate
   - Email 2: Contractor response with pricing

7. **Insurance Inquiry** (Responsive, No Exemption)
   - From: Jennifer Walsh to insurance company
   - Subject: "Claim inquiry - roof leak damage coverage"

### Request 2: Change Order #3 Documents (9 emails)
**CPRA Request**: "All documents regarding Change Order #3 and the agency's decision to approve or deny it"

**Required Emails**:
1. **Change Order Proposal** (Responsive, No Exemption)
   - From: Rachel Green to Sarah Chen
   - Subject: "Change Order #3 - Electrical system upgrade"
   - Content: Formal change order proposal with cost breakdown

2. **Technical Review** (Responsive, No Exemption)
   - From: Maria Santos to Mike Rodriguez  
   - Subject: "Technical review - Change Order #3 electrical requirements"
   - Content: Professional technical assessment

3. **Budget Impact Analysis** (Responsive, Deliberative Process)
   - From: Sarah Chen to David Kim
   - Subject: "INTERNAL: Budget implications of Change Order #3"
   - Content: Internal cost analysis and budget impact discussion

4. **Legal Review Chain** (Responsive, Attorney-Client Privilege, 3-email chain)
   - Email 1: Request for legal review of change order
   - Email 2: Attorney questions about contract terms
   - Email 3: Final legal recommendations on approval

5. **Approval Decision** (Responsive, No Exemption)
   - From: David Kim to Rachel Green
   - Subject: "Change Order #3 - Approved with conditions"
   - Content: Official approval notification

6. **Implementation Timeline** (Responsive, No Exemption)
   - From: Tony Martinez to project team
   - Subject: "Change Order #3 implementation schedule"

### Request 3: Internal Communications About Delays (7 emails)
**CPRA Request**: "All internal communications about project delays between January and March 2024"

**Required Emails**:
1. **Weather Delay Report** (Responsive, No Exemption)
   - From: Steve Wilson to Tony Martinez
   - Subject: "Weekly delay report - weather impacts"
   - Content: Report on weather-related construction delays

2. **Material Shortage Discussion** (Responsive, Deliberative Process)
   - From: Sarah Chen to Mike Rodriguez
   - Subject: "DRAFT: Strategy for material shortage delays"
   - Content: Internal discussion of delay management options

3. **Personnel Change Notification** (Responsive, Personnel Records)
   - From: Lisa Thompson to team
   - Subject: "Project manager transition - confidential"
   - Content: Information about Sarah Chen's reassignment, contains employee details

4. **Schedule Recovery Plan** (Responsive, No Exemption)
   - From: Jennifer Walsh to David Kim
   - Subject: "Project recovery timeline proposal"
   - Content: Proposed schedule adjustments and recovery strategies

5. **Contractor Performance Review** (Responsive, Deliberative Process)
   - From: Mike Rodriguez to David Kim
   - Subject: "INTERNAL: Contractor performance concerns"
   - Content: Internal assessment of contractor delays

6. **Budget Reallocation** (Responsive, Personnel Records)
   - From: David Kim to Lisa Thompson
   - Subject: "Budget adjustments - employee overtime approval"
   - Content: Personnel cost discussions with employee salary information

7. **Client Communication Strategy** (Responsive, Deliberative Process)
   - From: Sarah Chen to David Kim
   - Subject: "CONFIDENTIAL: Public communication about delays"
   - Content: Internal strategy for managing public messaging

### Non-Responsive Emails (6 emails)

**Required Emails**:
1. **Unrelated City Business** - Parks department budget discussion
2. **Personal Administrative** - Employee vacation request
3. **Different Project** - Library renovation status update  
4. **Vendor Marketing** - Equipment supplier promotional email
5. **Training Announcement** - Safety training schedule notification
6. **Office Administrative** - General office policy update

---

## Email Content Guidelines

### Realistic Email Elements
- **Headers**: Consistent timestamp formats, realistic email signatures
- **Tone Variety**: Mix of formal, semi-formal, and urgent communications
- **Length Variation**: Range from brief status updates to detailed technical reports
- **Attachment References**: Mention attachments without including actual files
- **Thread Continuity**: Ensure email chains reference previous messages logically

### Exemption Trigger Design

#### Attorney-Client Privilege Triggers
- **Law firm domains**: @sterlingmunicipallaw.com, @contractordefense.com
- **Privilege markings**: "PRIVILEGED AND CONFIDENTIAL", "ATTORNEY-CLIENT PRIVILEGE"
- **Legal advice language**: "legal recommendations", "liability exposure", "contract interpretation"

#### Personnel Records Triggers
- **Employee information**: Social Security numbers (XXX-XX-XXXX), salary figures
- **Performance data**: "performance review", "disciplinary action", "employee evaluation"
- **HR communications**: From/to HR representatives about specific employees

#### Deliberative Process Triggers
- **Decision-making language**: "internal discussion", "strategy", "options analysis"
- **Draft indicators**: "DRAFT", "preliminary", "for internal review only"
- **Confidential markings**: "INTERNAL USE ONLY", "CONFIDENTIAL"

### Quality Control Requirements
- **Consistency**: Maintain character voice and project timeline coherence
- **Realism**: Include realistic project management challenges and responses
- **Clarity**: Ensure exemption triggers are obvious but not artificially placed
- **Completeness**: Each email should feel like part of authentic project communication

---

## Generation Instructions for AI

### Output Format
Generate emails in a single text file WITHOUT separator lines between emails. The parser identifies new emails by the "From:" header at the beginning of a line. DO NOT include "---" or any other separator lines between emails - just start the next email immediately with its "From:" header.

### Content Generation Approach
1. **Establish Timeline**: Create emails chronologically from January to July 2024
2. **Develop Narrative**: Build coherent story around construction project challenges
3. **Character Consistency**: Maintain consistent voice and role for each participant
4. **Natural Integration**: Weave exemption triggers naturally into realistic business communications
5. **Chain Logic**: Ensure email chains reference previous messages and maintain logical flow

### Validation Checklist
- [ ] All 30 emails generated with proper formatting (From, To, Date, Subject headers)
- [ ] NO separator lines between emails (no "---", no "====", no blank separator lines)
- [ ] Each email starts with "From:" at the beginning of a line
- [ ] Date format follows: "Day, DD Mon YYYY HH:MM:SS -0800" (e.g., "Mon, 15 Jan 2024 09:30:00 -0800")
- [ ] Responsiveness distribution matches requirements
- [ ] Exemption triggers clearly present but realistic
- [ ] Email chains maintain logical threading with "RE:" or "Re:" subjects
- [ ] Timeline consistency maintained (January-July 2024)
- [ ] Professional business communication tone throughout
- [ ] No obvious "test data" artifacts that would break demo illusion

### Final Output
Single text file named `synthetic_emails.txt` ready for application ingestion, containing all 30 emails in proper format WITHOUT separator lines between emails.