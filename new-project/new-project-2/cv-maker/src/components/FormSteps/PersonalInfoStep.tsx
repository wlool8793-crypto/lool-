import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCV } from '@/contexts/CVContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Label } from '@/components/common/Label';
import { Button } from '@/components/common/Button';
import { User, Mail, Phone, MapPin, Globe, Github, Linkedin } from 'lucide-react';

const personalInfoSchema = z.object({
  fullName: z.string().min(1, 'Full name is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string().min(1, 'Phone number is required'),
  address: z.string().min(1, 'Address is required'),
  linkedin: z.string().url('Invalid LinkedIn URL').optional().or(z.literal('')),
  website: z.string().url('Invalid website URL').optional().or(z.literal('')),
  github: z.string().url('Invalid GitHub URL').optional().or(z.literal('')),
});

type PersonalInfoFormData = z.infer<typeof personalInfoSchema>;

export const PersonalInfoStep: React.FC = () => {
  const { state, dispatch } = useCV();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PersonalInfoFormData>({
    resolver: zodResolver(personalInfoSchema),
    defaultValues: state.cvData.personalInfo,
  });

  
  const onSubmit = (data: PersonalInfoFormData) => {
    dispatch({ type: 'UPDATE_PERSONAL_INFO', payload: data });
    dispatch({ type: 'SET_CURRENT_STEP', payload: 'summary' });
  };

  const handlePrevious = () => {
    // No previous step for personal info
  };

  const fields = [
    {
      name: 'fullName' as keyof PersonalInfoFormData,
      label: 'Full Name',
      placeholder: 'John Doe',
      icon: User,
      required: true,
    },
    {
      name: 'email' as keyof PersonalInfoFormData,
      label: 'Email Address',
      placeholder: 'john.doe@example.com',
      icon: Mail,
      required: true,
    },
    {
      name: 'phone' as keyof PersonalInfoFormData,
      label: 'Phone Number',
      placeholder: '+1 (555) 123-4567',
      icon: Phone,
      required: true,
    },
    {
      name: 'address' as keyof PersonalInfoFormData,
      label: 'Address',
      placeholder: '123 Main St, City, State 12345',
      icon: MapPin,
      required: true,
    },
    {
      name: 'linkedin' as keyof PersonalInfoFormData,
      label: 'LinkedIn Profile',
      placeholder: 'https://linkedin.com/in/johndoe',
      icon: Linkedin,
      required: false,
    },
    {
      name: 'website' as keyof PersonalInfoFormData,
      label: 'Personal Website',
      placeholder: 'https://johndoe.com',
      icon: Globe,
      required: false,
    },
    {
      name: 'github' as keyof PersonalInfoFormData,
      label: 'GitHub Profile',
      placeholder: 'https://github.com/johndoe',
      icon: Github,
      required: false,
    },
  ];

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          Personal Information
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fields.map((field) => {
              const Icon = field.icon;
              return (
                <div key={field.name} className="space-y-2">
                  <Label htmlFor={field.name} className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    {field.label}
                    {field.required && <span className="text-red-500">*</span>}
                  </Label>
                  <Input
                    id={field.name}
                    {...register(field.name)}
                    placeholder={field.placeholder}
                    variant={errors[field.name] ? 'error' : 'default'}
                  />
                  {errors[field.name] && (
                    <p className="text-sm text-red-500">{errors[field.name]?.message}</p>
                  )}
                </div>
              );
            })}
          </div>

          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={handlePrevious} disabled>
              Previous
            </Button>
            <Button type="submit">Next Step</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};