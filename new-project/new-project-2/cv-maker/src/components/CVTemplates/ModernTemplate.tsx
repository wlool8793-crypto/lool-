import React from 'react';
import type { CVData } from '@/types/cv';
import { formatDate } from '@/utils/pdfExport';
import { Mail, Phone, MapPin, Globe, Github, Linkedin } from 'lucide-react';

interface ModernTemplateProps {
  data: CVData;
}

export const ModernTemplate: React.FC<ModernTemplateProps> = ({ data }) => {
  const skillsByCategory = data.skills.reduce((acc, skill) => {
    if (!acc[skill.category]) {
      acc[skill.category] = [];
    }
    acc[skill.category].push(skill);
    return acc;
  }, {} as Record<string, typeof data.skills>);

  return (
    <div id="cv-preview" className="cv-container w-full max-w-4xl mx-auto bg-white shadow-lg">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{data.personalInfo.fullName}</h1>
            <div className="flex flex-wrap gap-4 text-sm">
              {data.personalInfo.email && (
                <div className="flex items-center gap-1">
                  <Mail className="h-4 w-4" />
                  {data.personalInfo.email}
                </div>
              )}
              {data.personalInfo.phone && (
                <div className="flex items-center gap-1">
                  <Phone className="h-4 w-4" />
                  {data.personalInfo.phone}
                </div>
              )}
              {data.personalInfo.address && (
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {data.personalInfo.address}
                </div>
              )}
            </div>
            <div className="flex flex-wrap gap-4 text-sm mt-2">
              {data.personalInfo.linkedin && (
                <div className="flex items-center gap-1">
                  <Linkedin className="h-4 w-4" />
                  LinkedIn
                </div>
              )}
              {data.personalInfo.github && (
                <div className="flex items-center gap-1">
                  <Github className="h-4 w-4" />
                  GitHub
                </div>
              )}
              {data.personalInfo.website && (
                <div className="flex items-center gap-1">
                  <Globe className="h-4 w-4" />
                  Website
                </div>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl font-bold text-blue-600">
                {data.personalInfo.fullName
                  .split(' ')
                  .map(n => n[0])
                  .join('')
                  .substring(0, 2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8">
        {/* Professional Summary */}
        {data.professionalSummary && (
          <div className="cv-section">
            <h2 className="cv-title text-blue-600">Professional Summary</h2>
            <p className="cv-text">{data.professionalSummary}</p>
          </div>
        )}

        {/* Work Experience */}
        {data.workExperience.length > 0 && (
          <div className="cv-section">
            <h2 className="cv-title text-blue-600">Work Experience</h2>
            {data.workExperience.map((exp) => (
              <div key={exp.id} className="mb-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="cv-subtitle">{exp.position}</h3>
                    <p className="text-blue-600 font-medium">{exp.company}</p>
                  </div>
                  <div className="text-right">
                    <p className="cv-date font-medium">
                      {formatDate(exp.startDate)} - {exp.current ? 'Present' : formatDate(exp.endDate)}
                    </p>
                  </div>
                </div>
                <p className="cv-text mt-2">{exp.description}</p>
                {exp.achievements.length > 0 && (
                  <ul className="list-disc list-inside mt-2 text-gray-700">
                    {exp.achievements.map((achievement, i) => (
                      <li key={i} className="text-sm">{achievement}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Education */}
        {data.education.length > 0 && (
          <div className="cv-section">
            <h2 className="cv-title text-blue-600">Education</h2>
            {data.education.map((edu) => (
              <div key={edu.id} className="mb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="cv-subtitle">{edu.degree} in {edu.field}</h3>
                    <p className="text-blue-600 font-medium">{edu.institution}</p>
                    {edu.gpa && <p className="text-sm text-gray-600">GPA: {edu.gpa}</p>}
                    {edu.honors && <p className="text-sm text-gray-600">{edu.honors}</p>}
                  </div>
                  <div className="text-right">
                    <p className="cv-date font-medium">
                      {formatDate(edu.startDate)} - {formatDate(edu.endDate)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Skills */}
        {data.skills.length > 0 && (
          <div className="cv-section">
            <h2 className="cv-title text-blue-600">Skills</h2>
            {Object.entries(skillsByCategory).map(([category, skills]) => (
              <div key={category} className="mb-4">
                <h3 className="font-semibold text-gray-800 mb-2 capitalize">{category}</h3>
                <div className="flex flex-wrap gap-2">
                  {skills.map((skill) => (
                    <span
                      key={skill.id}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {skill.name}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Projects */}
        {data.projects.length > 0 && (
          <div className="cv-section">
            <h2 className="cv-title text-blue-600">Projects</h2>
            {data.projects.map((project) => (
              <div key={project.id} className="mb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="cv-subtitle">{project.title}</h3>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {project.technologies.map((tech, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="cv-date font-medium">
                      {formatDate(project.startDate)}
                      {project.endDate && ` - ${formatDate(project.endDate)}`}
                    </p>
                  </div>
                </div>
                <p className="cv-text mt-2">{project.description}</p>
                {project.achievements.length > 0 && (
                  <ul className="list-disc list-inside mt-2 text-gray-700">
                    {project.achievements.map((achievement, i) => (
                      <li key={i} className="text-sm">{achievement}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Certifications */}
        {data.certifications.length > 0 && (
          <div className="cv-section">
            <h2 className="cv-title text-blue-600">Certifications</h2>
            {data.certifications.map((cert) => (
              <div key={cert.id} className="mb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="cv-subtitle">{cert.name}</h3>
                    <p className="text-blue-600 font-medium">{cert.issuer}</p>
                    {cert.credentialId && (
                      <p className="text-sm text-gray-600">ID: {cert.credentialId}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="cv-date font-medium">{formatDate(cert.issueDate)}</p>
                    {cert.expiryDate && (
                      <p className="text-sm text-gray-600">
                        Expires: {formatDate(cert.expiryDate)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Languages */}
        {data.languages.length > 0 && (
          <div className="cv-section">
            <h2 className="cv-title text-blue-600">Languages</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {data.languages.map((lang) => (
                <div key={lang.id}>
                  <h3 className="font-medium">{lang.name}</h3>
                  <p className="text-sm text-gray-600 capitalize">{lang.proficiency}</p>
                  {lang.certification && (
                    <p className="text-xs text-gray-500">{lang.certification}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};