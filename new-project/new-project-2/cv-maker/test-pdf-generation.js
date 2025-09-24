import { MarriagePDFGenerator } from '../src/utils/marriagePDFGenerator';

// Mock marriage data for testing
const mockMarriageData = {
  personalInfo: {
    fullName: "Test User",
    gender: "male" as const,
    dateOfBirth: "1990-01-01",
    age: 34,
    height: "5'10\"",
    weight: "70kg",
    bloodGroup: "O+",
    complexion: "fair",
    maritalStatus: "never_married" as const,
    religion: "Hindu",
    motherTongue: "Hindi",
    caste: "General",
    subcaste: "",
    nationality: "Indian",
    birthPlace: "Delhi",
    birthTime: "10:30 AM",
    gotra: "Bharadwaj",
    manglik: "no" as const,
    rashi: "Mesha",
    nakshatra: "Ashwini",
    aboutMe: "I am a software engineer looking for a suitable partner."
  },
  contactInfo: {
    email: "test@example.com",
    phone: "+91 9876543210",
    address: "123 Main Street, Delhi, India",
    alternatePhone: "",
    whatsappNumber: "+91 9876543210",
    preferredContactTime: "10 AM - 6 PM"
  },
  familyInfo: {
    familyType: "nuclear" as const,
    familyStatus: "middle_class" as const,
    familyValues: "moderate" as const,
    fatherName: "Father Name",
    fatherOccupation: "Businessman",
    fatherStatus: "alive" as const,
    motherName: "Mother Name",
    motherOccupation: "Homemaker",
    motherStatus: "alive" as const,
    brothers: 1,
    marriedBrothers: 0,
    sisters: 1,
    marriedSisters: 0,
    familyLocation: "Delhi, India",
    familyOrigin: "Delhi",
    maternalUncle: "",
    parentalProperty: "Own house"
  }
};

// Test PDF generation
async function testPDFGeneration() {
  console.log('🧪 Testing PDF Generation...');

  try {
    // Create a test div element
    const testDiv = document.createElement('div');
    testDiv.innerHTML = `
      <div style="font-family: Arial; padding: 20px;">
        <h1>Marriage Biodata Test</h1>
        <p>Name: ${mockMarriageData.personalInfo.fullName}</p>
        <p>Age: ${mockMarriageData.personalInfo.age}</p>
        <p>Religion: ${mockMarriageData.personalInfo.religion}</p>
        <p>Occupation: Software Engineer</p>
      </div>
    `;

    document.body.appendChild(testDiv);

    // Test PDF generation
    const pdfBlob = await MarriagePDFGenerator.generatePDF(
      testDiv,
      mockMarriageData as any,
      {
        template: 'traditional',
        quality: 'high',
        includeWatermark: true,
        language: 'en'
      }
    );

    console.log('✅ PDF generated successfully!', pdfBlob);

    // Test download
    await MarriagePDFGenerator.downloadPDF(
      testDiv,
      mockMarriageData as any,
      'test_marriage_biodata.pdf',
      {
        template: 'traditional',
        quality: 'high',
        includeWatermark: true,
        language: 'en'
      }
    );

    console.log('✅ PDF download test completed!');

    // Test preview
    await MarriagePDFGenerator.previewPDF(
      testDiv,
      mockMarriageData as any,
      {
        template: 'traditional',
        quality: 'high',
        includeWatermark: true,
        language: 'en'
      }
    );

    console.log('✅ PDF preview test completed!');

    // Cleanup
    document.body.removeChild(testDiv);

  } catch (error) {
    console.error('❌ PDF generation test failed:', error);
  }
}

// Test file size estimation
async function testFileSizeEstimation() {
  console.log('🧪 Testing File Size Estimation...');

  try {
    const testDiv = document.createElement('div');
    testDiv.innerHTML = `
      <div style="font-family: Arial; padding: 20px;">
        <h1>Test Document</h1>
        <p>This is a test document for file size estimation.</p>
      </div>
    `;

    document.body.appendChild(testDiv);

    const estimatedSize = await MarriagePDFGenerator.estimateFileSize(testDiv, 'high');
    console.log('✅ Estimated file size:', estimatedSize);

    document.body.removeChild(testDiv);

  } catch (error) {
    console.error('❌ File size estimation test failed:', error);
  }
}

// Run all tests
export async function runAllPDFTests() {
  console.log('🚀 Starting PDF Generation Tests...');

  await testPDFGeneration();
  await testFileSizeEstimation();

  console.log('🎉 All PDF tests completed!');
}

// Auto-run if this is the main module
if (typeof window !== 'undefined') {
  // Add a test button to the page for manual testing
  const testButton = document.createElement('button');
  testButton.textContent = 'Test PDF Generation';
  testButton.style.position = 'fixed';
  testButton.style.top = '10px';
  testButton.style.right = '10px';
  testButton.style.zIndex = '9999';
  testButton.style.padding = '10px';
  testButton.style.backgroundColor = '#007bff';
  testButton.style.color = 'white';
  testButton.style.border = 'none';
  testButton.style.borderRadius = '5px';
  testButton.style.cursor = 'pointer';

  testButton.addEventListener('click', runAllPDFTests);
  document.body.appendChild(testButton);

  console.log('🧪 PDF Test button added to page. Click to test PDF generation.');
}