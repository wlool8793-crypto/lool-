import React from 'react';
import type { CVData } from '@/types/cv';
import { formatDate } from '@/utils/pdfExport';
import { Mail, Phone, MapPin, Globe, Github, Linkedin } from 'lucide-react';

interface TraditionalTemplateProps {
  data: CVData;
}

export const TraditionalTemplate: React.FC<TraditionalTemplateProps> = ({ data }) => {
  const skillsByCategory = data.skills.reduce((acc, skill) => {
    if (!acc[skill.category]) {
      acc[skill.category] = [];
    }
    acc[skill.category].push(skill);
    return acc;
  }, {} as Record<string, typeof data.skills>);

  return (
    <div id="cv-preview" className="cv-container w-full max-w-4xl mx-auto bg-white shadow-lg border-2 border-gray-800">
      {/* Header Section */}
      <div className="bg-gray-800 text-white p-8 text-center">
        <h1 className="text-4xl font-bold mb-2 uppercase tracking-wide">
          {data.personalInfo.fullName}
        </h1>
        <div className="flex flex-wrap justify-center gap-6 text-sm mt-4">
          {data.personalInfo.email && (
            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4" />
              {data.personalInfo.email}
            </div>
          )}
          {data.personalInfo.phone && (
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4" />
              {data.personalInfo.phone}
            </div>
          )}
          {data.personalInfo.address && (
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              {data.personalInfo.address}
            </div>
          )}
        </div>
        <div className="flex flex-wrap justify-center gap-6 text-sm mt-2">
          {data.personalInfo.linkedin && (
            <div className="flex items-center gap-2">
              <Linkedin className="h-4 w-4" />
              LinkedIn
            </div>
          )}
          {data.personalInfo.github && (
            <div className="flex items-center gap-2">
              <Github className="h-4 w-4" />
              GitHub
            </div>
          )}
          {data.personalInfo.website && (
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Website
            </div>
          )}
        </div>
      </div>

      <div className="p-8">
        {/* Professional Summary */}
        {data.professionalSummary && (
          <div className="cv-section mb-8">
            <h2 className="cv-title text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-gray-800 uppercase">
              Professional Summary
            </h2>
            <p className="cv-text text-gray-700 leading-relaxed">{data.professionalSummary}</p>
          </div>
        )}

        {/* Work Experience */}
        {data.workExperience.length > 0 && (
          <div className="cv-section mb-8">
            <h2 className="cv-title text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-gray-800 uppercase">
              Work Experience
            </h2>
            {data.workExperience.map((exp) => (
              <div key={exp.id} className="mb-6 pb-6 border-l-2 border-gray-300 pl-6">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="cv-subtitle text-xl font-semibold text-gray-800">{exp.position}</h3>
                    <p className="text-gray-600 font-medium">{exp.company}</p>
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-sm font-medium text-gray-600">
                      {formatDate(exp.startDate)} - {exp.current ? 'Present' : formatDate(exp.endDate)}
                    </p>
                  </div>
                </div>
                <p className="cv-text text-gray-700 leading-relaxed mb-3">{exp.description}</p>
                {exp.achievements.length > 0 && (
                  <ul className="list-disc list-inside text-gray-700 space-y-1">
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
          <div className="cv-section mb-8">
            <h2 className="cv-title text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-gray-800 uppercase">
              Education
            </h2>
            {data.education.map((edu) => (
              <div key={edu.id} className="mb-4 pb-4 border-l-2 border-gray-300 pl-6">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="cv-subtitle text-xl font-semibold text-gray-800">
                      {edu.degree} in {edu.field}
                    </h3>
                    <p className="text-gray-600 font-medium">{edu.institution}</p>
                    {edu.gpa && <p className="text-sm text-gray-600 mt-1">GPA: {edu.gpa}</p>}
                    {edu.honors && <p className="text-sm text-gray-600 mt-1">{edu.honors}</p>}
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-sm font-medium text-gray-600">
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
          <div className="cv-section mb-8">
            <h2 className="cv-title text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-gray-800 uppercase">
              Skills
            </h2>
            {Object.entries(skillsByCategory).map(([category, skills]) => (
              <div key={category} className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3 text-lg border-b border-gray-300 pb-1">
                  {category}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {skills.map((skill) => (
                    <span
                      key={skill.id}
                      className="px-4 py-2 bg-gray-100 text-gray-800 rounded text-sm font-medium border border-gray-300"
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
          <div className="cv-section mb-8">
            <h2 className="cv-title text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-gray-800 uppercase">
              Projects
            </h2>
            {data.projects.map((project) => (
              <div key={project.id} className="mb-6 pb-6 border-l-2 border-gray-300 pl-6">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="cv-subtitle text-xl font-semibold text-gray-800">{project.title}</h3>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {project.technologies.map((tech, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs font-medium"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-sm font-medium text-gray-600">
                      {formatDate(project.startDate)}
                      {project.endDate && ` - ${formatDate(project.endDate)}`}
                    </p>
                  </div>
                </div>
                <p className="cv-text text-gray-700 leading-relaxed mb-3">{project.description}</p>
                {project.achievements.length > 0 && (
                  <ul className="list-disc list-inside text-gray-700 space-y-1">
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
          <div className="cv-section mb-8">
            <h2 className="cv-title text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-gray-800 uppercase">
              Certifications
            </h2>
            {data.certifications.map((cert) => (
              <div key={cert.id} className="mb-4 pb-4 border-l-2 border-gray-300 pl-6">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="cv-subtitle text-xl font-semibold text-gray-800">{cert.name}</h3>
                    <p className="text-gray-600 font-medium">{cert.issuer}</p>
                    {cert.credentialId && (
                      <p className="text-sm text-gray-600 mt-1">ID: {cert.credentialId}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="cv-date text-sm font-medium text-gray-600">
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
            <h2 className="cv-title text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-gray-800 uppercase">
              Languages
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {data.languages.map((lang) => (
                <div key={lang.id} className="border-l-2 border-gray-300 pl-4">
                  <h3 className="font-medium text-gray-800">{lang.name}</h3>
                  <p className="text-sm text-gray-600 capitalize">{lang.proficiency}</p>
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