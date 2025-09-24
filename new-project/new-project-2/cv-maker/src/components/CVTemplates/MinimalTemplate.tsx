import React from 'react';
import type { CVData } from '@/types/cv';
import { formatDate } from '@/utils/pdfExport';
import { Mail, Phone, MapPin, Globe, Github, Linkedin } from 'lucide-react';

interface MinimalTemplateProps {
  data: CVData;
}

export const MinimalTemplate: React.FC<MinimalTemplateProps> = ({ data }) => {
  const skillsByCategory = data.skills.reduce((acc, skill) => {
    if (!acc[skill.category]) {
      acc[skill.category] = [];
    }
    acc[skill.category].push(skill);
    return acc;
  }, {} as Record<string, typeof data.skills>);

  return (
    <div id="cv-preview" className="cv-container w-full max-w-4xl mx-auto bg-white shadow-sm">
      {/* Header Section */}
      <div className="p-8 pb-4">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-light text-gray-900 mb-2">
            {data.personalInfo.fullName}
          </h1>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
            {data.personalInfo.email && (
              <div className="flex items-center gap-1">
                <Mail className="h-3 w-3" />
                {data.personalInfo.email}
              </div>
            )}
            {data.personalInfo.phone && (
              <div className="flex items-center gap-1">
                <Phone className="h-3 w-3" />
                {data.personalInfo.phone}
              </div>
            )}
            {data.personalInfo.address && (
              <div className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {data.personalInfo.address}
              </div>
            )}
            {data.personalInfo.linkedin && (
              <div className="flex items-center gap-1">
                <Linkedin className="h-3 w-3" />
                LinkedIn
              </div>
            )}
            {data.personalInfo.github && (
              <div className="flex items-center gap-1">
                <Github className="h-3 w-3" />
                GitHub
              </div>
            )}
            {data.personalInfo.website && (
              <div className="flex items-center gap-1">
                <Globe className="h-3 w-3" />
                Website
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="px-8 pb-8">
        {/* Professional Summary */}
        {data.professionalSummary && (
          <div className="cv-section mb-6">
            <h2 className="cv-title text-lg font-medium text-gray-900 mb-2 uppercase tracking-wide">
              Summary
            </h2>
            <p className="cv-text text-gray-700 leading-relaxed text-sm">{data.professionalSummary}</p>
          </div>
        )}

        {/* Work Experience */}
        {data.workExperience.length > 0 && (
          <div className="cv-section mb-6">
            <h2 className="cv-title text-lg font-medium text-gray-900 mb-4 uppercase tracking-wide">
              Experience
            </h2>
            {data.workExperience.map((exp) => (
              <div key={exp.id} className="mb-4">
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h3 className="cv-subtitle font-medium text-gray-900">{exp.position}</h3>
                    <p className="text-gray-600 text-sm">{exp.company}</p>
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-xs text-gray-600">
                      {formatDate(exp.startDate)} - {exp.current ? 'Present' : formatDate(exp.endDate)}
                    </p>
                  </div>
                </div>
                <p className="cv-text text-gray-700 text-sm leading-relaxed mb-2">{exp.description}</p>
                {exp.achievements.length > 0 && (
                  <ul className="list-disc list-inside text-gray-700 text-xs space-y-1 ml-4">
                    {exp.achievements.map((achievement, i) => (
                      <li key={i}>{achievement}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Education */}
        {data.education.length > 0 && (
          <div className="cv-section mb-6">
            <h2 className="cv-title text-lg font-medium text-gray-900 mb-4 uppercase tracking-wide">
              Education
            </h2>
            {data.education.map((edu) => (
              <div key={edu.id} className="mb-3">
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h3 className="cv-subtitle font-medium text-gray-900">
                      {edu.degree} in {edu.field}
                    </h3>
                    <p className="text-gray-600 text-sm">{edu.institution}</p>
                    {edu.gpa && <p className="text-xs text-gray-600 mt-1">GPA: {edu.gpa}</p>}
                    {edu.honors && <p className="text-xs text-gray-600 mt-1">{edu.honors}</p>}
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-xs text-gray-600">
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
          <div className="cv-section mb-6">
            <h2 className="cv-title text-lg font-medium text-gray-900 mb-4 uppercase tracking-wide">
              Skills
            </h2>
            {Object.entries(skillsByCategory).map(([category, skills]) => (
              <div key={category} className="mb-4">
                <h3 className="font-medium text-gray-800 mb-2 text-sm uppercase tracking-wide">
                  {category}
                </h3>
                <p className="text-sm text-gray-700">
                  {skills.map((skill) => skill.name).join(' • ')}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Projects */}
        {data.projects.length > 0 && (
          <div className="cv-section mb-6">
            <h2 className="cv-title text-lg font-medium text-gray-900 mb-4 uppercase tracking-wide">
              Projects
            </h2>
            {data.projects.map((project) => (
              <div key={project.id} className="mb-4">
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h3 className="cv-subtitle font-medium text-gray-900">{project.title}</h3>
                    <p className="text-xs text-gray-600 mt-1">
                      {project.technologies.join(' • ')}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-xs text-gray-600">
                      {formatDate(project.startDate)}
                      {project.endDate && ` - ${formatDate(project.endDate)}`}
                    </p>
                  </div>
                </div>
                <p className="cv-text text-gray-700 text-sm leading-relaxed mb-2">{project.description}</p>
                {project.achievements.length > 0 && (
                  <ul className="list-disc list-inside text-gray-700 text-xs space-y-1 ml-4">
                    {project.achievements.map((achievement, i) => (
                      <li key={i}>{achievement}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Certifications */}
        {data.certifications.length > 0 && (
          <div className="cv-section mb-6">
            <h2 className="cv-title text-lg font-medium text-gray-900 mb-4 uppercase tracking-wide">
              Certifications
            </h2>
            {data.certifications.map((cert) => (
              <div key={cert.id} className="mb-3">
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h3 className="cv-subtitle font-medium text-gray-900">{cert.name}</h3>
                    <p className="text-gray-600 text-sm">{cert.issuer}</p>
                    {cert.credentialId && (
                      <p className="text-xs text-gray-600 mt-1">ID: {cert.credentialId}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-xs text-gray-600">
                      {formatDate(cert.issueDate)}
                    </p>
                    {cert.expiryDate && (
                      <p className="text-xs text-gray-500">
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
            <h2 className="cv-title text-lg font-medium text-gray-900 mb-4 uppercase tracking-wide">
              Languages
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {data.languages.map((lang) => (
                <div key={lang.id}>
                  <h3 className="font-medium text-gray-800 text-sm">{lang.name}</h3>
                  <p className="text-xs text-gray-600 capitalize">{lang.proficiency}</p>
                  {lang.certification && (
                    <p className="text-xs text-gray-500 mt-1">{lang.certification}</p>
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